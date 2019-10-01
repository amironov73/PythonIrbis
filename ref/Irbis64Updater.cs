using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Threading;
using ManagedClient;

namespace WebIrbisNet.Irbis64
{
    /// <summary>
    /// Утилита для обновления баз данных ирбис
    /// </summary>
    public class Irbis64Updater : Irbis64AbstractUpdater, IDisposable
    {
        /// <summary>
        /// Контейнер для связи списка ссылок с блоком N01 / L01
        /// </summary>
        private class NodeItemTermLinksPair
        {
            public TermLink[] Links { get; set; }
            public NodeItem Item { get; set; }
        }

        private string _dbMst;
        private Mutex _dbSync;
        private IIrbis64IO _tmpIrbisIO;
        private string _tmpPath;

        public Irbis64Updater(string db)
            : this(db, false, true, true)
        {
        }

        public Irbis64Updater(string db, bool keepLock, bool ifUpdate, bool autoin)
            : this(db, keepLock, ifUpdate, autoin, autoin ? "autoin.gbl" : null)
        {
        }

        public Irbis64Updater(string db, bool keepLock, bool ifUpdate, bool autoin, string autoinFile)
            : base(db, keepLock, ifUpdate, autoin, autoinFile)
        {
            _dbMst = Irbis64Config.LookupDbMst(_dbName);
            _ownIrbisIO = true;
        }

        public override string DbName
        {
            get { return _dbName; }
            set
            {
                _dbName = value;
                if (_dbName != null)
                    _dbMst = Irbis64Config.LookupDbMst(_dbName);
                else
                    _dbMst = null;
            }
        }

        private void GetDirectIO()
        {
            _irbisIO = new IrbisDirectIO(_dbMst, true);
            _irbisIO.Irbis64Code += OnIrbis64Code;
        }

        private void CloseDirectIO()
        {
            if (_irbisIO != null)
            {
                _irbisIO.Irbis64Code -= OnIrbis64Code;
                _irbisIO.Dispose();
                _irbisIO = null;
            }
        }

        private void GetMutex()
        {
            bool createdNew;
            var mutexSecurity = new MutexSecurity();
            mutexSecurity.AddAccessRule(new MutexAccessRule(new SecurityIdentifier(WellKnownSidType.WorldSid, null),
                                                            MutexRights.Synchronize | MutexRights.Modify, AccessControlType.Allow));

            _dbSync = new Mutex(false, "IRBIS64_MUTEX" + _dbName, out createdNew, mutexSecurity);
            _dbSync.WaitOne();
            //return new Mutex(false, "IRBIS64_MUTEX" + db.ToUpper());
        }

        private void CloseMutex()
        {
            if (_dbSync != null)
            {
                _dbSync.ReleaseMutex();
                _dbSync.Dispose();
                _dbSync = null;
            }
        }

        protected override void BeginUpdate()
        {
            GetMutex();
            GetDirectIO();
        }

        protected override void EndUpdate(bool success)
        {
            CloseDirectIO();
            CloseMutex();
        }

        protected override void BlockUpdate()
        {
        }

        protected override void BeginWriteRecord(IrbisRecord rec)
        {
            //запись mst и xrf, статус записи проставляется как неактуализированный                            
            ((IrbisDirectIO)_irbisIO).WriteRecord(rec, true);
        }

        protected override void EndWriteRecord(IrbisRecord rec)
        {
            //обновление статуса в mst и xrf, проставляется статус актуализации
            //статус блокировки также снимается
            ((IrbisDirectIO)_irbisIO).SetRecordActualized(rec, _keepLock, _ifUpdate, true);
        }

        protected override void LockDatabase(bool flag)
        {
            ((IrbisDirectIO)_irbisIO).Mst.LockDatabase(flag);
        }

        protected override void DeleteRecord(IrbisRecord rec)
        {
            ((IrbisDirectIO)_irbisIO).DeleteRecord(rec, true);
        }

        protected override void UndeleteRecord(IrbisRecord rec)
        {
            //запись mst и xrf, статус записи проставляется как неактуализированный
            ((IrbisDirectIO)_irbisIO).UndeleteRecord(rec, true);
        }

        /// <summary>
        /// Инициализация новой базы
        /// </summary>
        public override void CreateDatabase(string db)
        {
            var dbPath = String.Format("{0}/{1}", Irbis64Config.DataPath, db);
            _dbMst = String.Format("{0}/{1}/{1}.mst", Irbis64Config.DataPath, db);
            if (!Directory.Exists(dbPath))
                Directory.CreateDirectory(dbPath);
            var tmpDb = _dbName;
            _dbName = db;
            try
            {
                InitDatabase();
            }
            finally
            {
                _dbName = tmpDb;
            }
        }

        /// <summary>
        /// Создание корневого блока
        /// </summary>
        private void CheckRootNode()
        {
            var directIO = (IrbisDirectIO)_irbisIO;
            //если n01 файл пустой, проинициализируем инвертный файл
            if (directIO.InvertedFile.N01.Length == 0)
                directIO.InvertedFile.CreateRootNode(true);
        }

        /// <summary>
        /// Поиск, проверка наличия и правильности старого ключа N01
        /// </summary>
        private SearchTermInfo SearchCheckNodeTerm(string text, int nodeNumber, int firstNodeNumber, Dictionary<int, NodeRecord> nodeRecords, List<NodeRecord> editNodes)
        {
            var directIO = ((IrbisDirectIO)_irbisIO);
            //поиск ближайшего термина в n01
            //var st = _directIO.InvertedFile.SearchNodeTerm(text, firstNodeNumber);
            //на самом нижнем уровне SearchNodeTerm будет работать долго, быстрее сделать обычный поиск по дереву
            //SearchTermInfo st = null;
            //if (firstNodeNumber > 1)
            //    st = _directIO.InvertedFile.SearchNodeTerm(text, firstNodeNumber);
            //else
            var st = directIO.InvertedFile.SearchClosestNode(text, firstNodeNumber);
            //если найденный ключ соответствует указанному
            if (st.Text == text)
            {
                //проверка блока следующего уровня n01 или l01 
                if (st.LeafNodeNumber != nodeNumber)
                {
                    //сделать проверку на целостность данных
                    //ирбис иногда оставляет ключи, которые никуда не ссылаются,
                    //если такой ключ есть, проверить ссылается ли он на следующий блок или на l01
                    //и совпадает ли этот ключ с первым ключом блока l01
                    //если ссылается и совпадает - ошибка
                    //у ключей, ссылающихся на leaf FullOffset отрицательный
                    //читаем n01 / l01
                    var checkNode = st.FullOffset < 0 ?
                        directIO.InvertedFile.ReadLeaf(st.LeafNodeNumber) :
                        directIO.InvertedFile.ReadNode(st.LeafNodeNumber);
                    //проверяем текст первого ключа, он должен быть равен ключу из n01
                    if (checkNode.Items[0].Text == st.Text)
                        throw new InvalidOperationException(String.Format("Ключ уже есть в n01 в другом блоке: item.text={0}, item.node={1}, st.text={2}, st.node={3}, st.leaf={4}", text, nodeNumber, st.Text, st.NodeNumber, st.LeafNodeNumber));
                }
                _logger.Debug(String.Format("Пропуск добавления, ключ уже есть в n01: item.text={0}, item.node={1}, st.text={2}, st.node={3}, st.leaf={4}", text, nodeNumber, st.Text, st.NodeNumber, st.LeafNodeNumber));
                return null;

                //                //если такой термин есть и соответствует требуемому блоку, то вернуть null
                //                if (!remove)
                //                {
                //                    _logger.Info(String.Format("Пропуск добавления, ключ уже есть в n01: item.text={0}, item.node={1}, st.text={2}, st.node={3}, первый блок {4}", text, nodeNumber, st.Text, st.NodeNumber, firstNodeNumber));
                //                    return null;
                //                }
                //                //удаление старого ключа, если есть
                //                NodeRecord node = null;
                //                if (!nodeRecords.TryGetValue(st.NodeNumber, out node))
                //                {
                //                    node = _directIO.InvertedFile.ReadNode(st.NodeNumber);
                //                    nodeRecords[st.NodeNumber] = node;
                //                }
                //                var items = node.Items;
                //#if TEXT_FIELDS
                //                if (node.BeginEdit())
                //                    editNodes.Add(node);
                //                for (int i = items.Length - 1; i >= 0; i--)

                //#else
                //                for (int i = items.Count - 1; i >=0; i--)
                //#endif
                //                {
                //                    if (items[i].Text == text)
                //                    {
                //                        //если удаляется первый ключ, то пометить блок, чтобы обновить вверх по дереву
                //                        //если блок стоит дальше первого на уровне, первый блок не имеет отдельных ключей
                //                        if (i == 0 && node.Leader.Previous > 0 && node.RemovingParentKey == null)
                //                            node.RemovingParentKey = text;
                //                        if (items.Length == 1)
                //                            throw new InvalidOperationException(String.Format("Удаление последнего ключа n01: key={0}, node={1}", items[i].Text, node.Leader.Number));
                //                        //_logger.Info(String.Format("Удаление старого ключа n01: key={0}, node={1}", items[i].Text, node.Leader.Number));
                //                        _logger.Info(String.Format("Удаление старого ключа n01: i={0}, node.number={1}, node.previous={2}, current node.number={3}, key={4}", i, node.Leader.Number, node.Leader.Previous, nodeNumber, items[i].Text));

                //#if TEXT_FIELDS
                //                        node.RemoveItemAt(i);
                //#else
                //                        node.Items.RemoveAt(i);
                //#endif
                //                        break;
                //                    }
                //                }
            }
            return st;
        }

        /// <summary>
        /// Обновление инвертного файла
        /// </summary>
        protected override void UpdateTerms(FstTermLink[] addTerms, FstTermLink[] removeTerms, bool rebuild)
        {
            var directIO = (IrbisDirectIO)_irbisIO;
            CheckRootNode();

            var nodeRecords = new Dictionary<int, NodeRecord>();
#if TEXT_FIELDS
            var editNodes = new List<NodeRecord>();
#endif

            //добавление терминов
            var addingItems = AddTerms(addTerms, nodeRecords);
            //удаление терминов
            var removingItems = RemoveTerms(removeTerms, addingItems, nodeRecords);

            //элементы в l01, которые надо как бы удалить остаются на месте, просто в лидере ifp записи проставляется 0 ссылок
            //сами элементы не удаляются 
            foreach (var kvp in removingItems)
            {
                var item = kvp.Value.Item;
                directIO.InvertedFile.WriteIfpRecord(item, null, false /*здесь только обнуление полей в заголовках, расширять не требуется*/);
            }

            //запись ifp идет первой, так как здесь в добавленных элементах обновляется ссылка на место в ifp
            foreach (var kvp in addingItems)
            {
                //var item = kvp.Value;
                //var links = kvp.Key.Links;
                var item = kvp.Value.Item;
                var links = kvp.Value.Links;
                directIO.InvertedFile.WriteIfpRecord(item, links, true);
            }

            var leafNodes = nodeRecords.Values.ToArray();
            nodeRecords.Clear();

            //запись блоков l01
            foreach (var leafNode in leafNodes)
            {
                //после пересортировки терминов в блоке первый может смениться, тогда надо обновить блоки вверх по дереву
                //обновляем блок
                var newNodes = directIO.InvertedFile.WriteLeaf(leafNode, rebuild, true);
                //при создании нового l01 блока первый его элемент становится новым элементом в n01 блока
                if (newNodes != null && newNodes.Length > 0)
                {
                    foreach (var newNode in newNodes)
                    {
                        //удаление ключа в n01, если первый ключ в l01 изменился
                        //if (newNode.RemovingParentKey != null)
                        //    SearchCheckNodeTerm(newNode.RemovingParentKey, newNode.Leader.Number, 1, true, nodeRecords, editNodes);
                        //var st = SearchCheckNodeTerm(newNode.Items[0].Text, newNode.Leader.Number, 1, false, nodeRecords, editNodes);
                        var st = SearchCheckNodeTerm(newNode.Items[0].Text, newNode.Leader.Number, 1, nodeRecords, editNodes);
                        //null вернется, если термин найден и соответствует требуемому блоку
                        if (st != null)
                        {
                            var nodeItem = new NodeItem
                            {
                                Text = newNode.Items[0].Text,
                                //отрицательный номер - ссылка на leaf
                                LowOffset = -newNode.Leader.Number,
                                NodeNumber = newNode.Leader.Number
                            };

                            //начитаем блок n01
                            NodeRecord node = null;
                            if (!nodeRecords.TryGetValue(st.NodeNumber, out node))
                            {
                                node = directIO.InvertedFile.ReadNode(st.NodeNumber);
                                nodeRecords[st.NodeNumber] = node;
                            }
                            //создадим новый ключ
#if TEXT_FIELDS
                            if (node.BeginEdit())
                                editNodes.Add(node);
                            node.AddItem(nodeItem);
#else
                        node.Items.Add(nodeItem);
#endif
                        }
                    }
                }

            }

#if TEXT_FIELDS
            //применим изменения в нодах
            foreach (var node in editNodes)
            {
                node.CommitEdit();
            }
            editNodes.Clear();
#endif

            //запись блоков n01, если есть
            var nodes = nodeRecords.Values.ToArray();
            //блоки n01, которые добавляются при расширении блоков в ключами
            var addedNodes = new List<NodeRecord>();
            foreach (var node in nodes)
            {
                var newNodes = directIO.InvertedFile.WriteNode(node, rebuild, true);
                if (newNodes != null && newNodes.Length > 0)
                    addedNodes.AddRange(newNodes);
            }
            //если есть новые блоки N01, требуется создать / обновить дерево оглавления снизу вверх
            //дерево оглавления - это блоки в N01, в которых каждый ключ - первый ключ из обычного блока
            //лидеры блоков оглаления указывают только на блоки оглавления, ключи - на обычные блоки с ключами
            //на вершину дерева оглавления указывает поле номера блока из первого блока (первые 4 байта в N01)
            //если этот номер не равен 1, это означает, что оглавление уже создано
            //оглавление создается, когда в N01 больше 1 блока
            //уровней оглавления может быть сколько угодно, это древовидная структура            
            if (addedNodes.Count > 0)
            {
                //здесь создается новый уровень только если дерева оглавления вообще нет
                //если только сменился первый ключ в блоке, новый уровень создавать не надо
                //var newLevel =
                //    addedNodes.Any(n => n.RemovingParentKey == null) ?
                //    _directIO.InvertedFile.ReadFirstNodeNumber() == 1 :
                //    false;
                var newLevel = directIO.InvertedFile.ReadFirstNodeNumber() == 1;
                UpdateTree(addedNodes.ToArray(), newLevel, rebuild, true);
                addedNodes.Clear();
            }

            nodeRecords.Clear();
            addingItems.Clear();
            removingItems.Clear();
        }

        /// <summary>
        /// Добавление новых терминов
        /// </summary>
        private Dictionary<string, NodeItemTermLinksPair> AddTerms(FstTermLink[] addTerms, Dictionary<int, NodeRecord> nodeRecords)
        {
            var directIO = (IrbisDirectIO)_irbisIO;
#if TEXT_FIELDS
            var editNodes = new List<NodeRecord>();
#endif
            //при добавлении терминов нужно поискать блоки в l01, куда можно поместить термин и пересоздать блоки
            //если база пустая, то на данный момент корневые блоки уже созданы и термины попадут в них
            //если терминов много, то группировка позволит выявить одинаковые и сократить время поиска
            var addingTermsByNode = addTerms.GroupBy(t => t.Term.ToUpperInvariant()).SelectMany(g =>
            {
                //второй горизонтальный обход нижнего уровня дерева может быть долгим 
                //var st = _directIO.InvertedFile.SearchTermExact(t.Term);
                ////если подходящего блока нет, назначим корневой, так как он был создан
                //if (st == null)
                //    st = _directIO.InvertedFile.SearchNodeTerm(t.Term);

                //так будет быстрее, данный метод ищет сразу l01, который пригоден для записи
                var st = directIO.InvertedFile.SearchClosestLeaf(g.Key, false);
                if (st == null)
                    st = directIO.InvertedFile.SearchClosestNode(g.Key, 1);
                //если подходящего блока нет, назначим корневой, так как он был создан
                //это имеет смысл только, когда в l01 только один свеже созданный блок
                //if (st == null)
                //    st = _directIO.InvertedFile.SearchNodeTerm(g.Key);
                return g.Select(t => new { t, st });
            })
            .Where(a => a.st != null).GroupBy(a => a.st.LeafNodeNumber, a => a.t).ToArray();
            var addingItems = new Dictionary<string, NodeItemTermLinksPair>();
            //добавление терминов
            foreach (var g in addingTermsByNode)
            {
                var nodeNumber = g.Key;
                var addingTerms = g.ToArray();
                //начитаем блок l01
                NodeRecord leafNode = null;
                if (!nodeRecords.TryGetValue(nodeNumber, out leafNode))
                {
                    leafNode = directIO.InvertedFile.ReadLeaf(nodeNumber);
                    nodeRecords[nodeNumber] = leafNode;
                }
                //добавим элементы с учетом задвоев терминов, выдаваемых FST
                foreach (var termG in addingTerms.GroupBy(t => t.Term.ToUpperInvariant()))
                {
                    var term = termG.Key;
                    //var termsByKey = termG.ToArray();
                    //var firstTermByKey = termsByKey[0];
                    var termLinks = termG.Select(l => l.Link).ToArray();
                    var nodeItem = leafNode.Items.Where(itm => itm.Text == term).FirstOrDefault();
                    if (nodeItem == null)
                    {
                        nodeItem = new NodeItem { Text = term };
#if TEXT_FIELDS
                        if (leafNode.BeginEdit())
                            editNodes.Add(leafNode);
                        leafNode.AddItem(nodeItem);
#else
                        leafNode.Items.Add(nodeItem);
#endif
                    }
                    else if (nodeItem.FullOffset >= 0)
                    {
                        //var termLinks = termsByKey.Length == 1 ? firstTermByKey.Links : termsByKey.SelectMany(t => t.Links).ToArray();
                        
                        //начитаем ссылки из существующего leaf элемента
                        var oldLinks = directIO.InvertedFile.ReadIfpRecordFull(nodeItem.FullOffset);
                        var newLinks = oldLinks.Union(termLinks).ToArray();
                        termLinks = newLinks;
                        //firstTermByKey.SetLinks(newLinks, false);
                        //проверка, если новые ссылки не добавлены, то такой термин в список на добавление не идет
                        if (newLinks.Length == oldLinks.Length)
                            continue;
                    }
                    //addingItems[firstTermByKey] = nodeItem;
                    addingItems[term] = new NodeItemTermLinksPair { Item = nodeItem, Links = termLinks }; 
                }
            }
#if TEXT_FIELDS
            foreach (var node in editNodes)
            {
                node.CommitEdit();
            }
            editNodes.Clear();
#endif
            return addingItems;
        }

        /// <summary>
        /// Удаление терминов
        /// </summary>
        private Dictionary<string, NodeItemTermLinksPair> RemoveTerms(FstTermLink[] removeTerms, Dictionary<string, NodeItemTermLinksPair> addingItems, Dictionary<int, NodeRecord> nodeRecords)
        {
            var directIO = (IrbisDirectIO)_irbisIO;
            //при удалении терминов нужно пересоздать блоки в l01, где они были
            //если терминов много, то группировка позволит выявить одинаковые термины и сократить время поиска
            var removingTermsByNode = removeTerms.GroupBy(t => t.Term.ToUpperInvariant()).SelectMany(g =>
            {
                var st = directIO.InvertedFile.SearchTermExact(g.Key);
                return g.Select(t => new { t, st });
            })
            .Where(a => a.st != null).GroupBy(a => a.st.LeafNodeNumber, a => a.t).ToArray();

            var removingItems = new Dictionary<string, NodeItemTermLinksPair>();

            //удаление терминов с учетом задвоев терминов, выдаваемых FST
            foreach (var g in removingTermsByNode)
            {
                var nodeNumber = g.Key;
                var removingTerms = g.ToArray();
                //начитаем блок l01
                NodeRecord leafNode = null;
                if (!nodeRecords.TryGetValue(nodeNumber, out leafNode))
                {
                    leafNode = directIO.InvertedFile.ReadLeaf(nodeNumber);
                    nodeRecords[nodeNumber] = leafNode;
                }
                //удалим элементы
                foreach (var termG in removingTerms.GroupBy(t => t.Term.ToUpperInvariant()))
                {
                    var term = termG.Key;
                    var nodeItem = leafNode.Items.Where(itm => itm.Text == term).FirstOrDefault();
                    if (nodeItem != null)
                    {
                        var termLinks = termG.Select(l => l.Link).ToArray();
                        //var termsByKey = termG.ToArray();
                        //var firstTermByKey = termsByKey[0];

                        if (nodeItem.FullOffset >= 0)
                        {
                            //var termLinks = termsByKey.Length == 1 ? firstTermByKey.Links : termsByKey.SelectMany(t => t.Links).ToArray();
                            var oldLinks = directIO.InvertedFile.ReadIfpRecordFull(nodeItem.FullOffset);
                            //если есть ссылки на другие записи, то надо перезаписать элемент, иначе почистить ссылки
                            var linksToAnotherRecords = oldLinks.Except(termLinks).Distinct().ToArray();
                            if (linksToAnotherRecords.Length > 0)
                            {
                                //firstTermByKey.SetLinks(linksToAnotherRecords);
                                //addingItems[firstTermByKey] = nodeItem;
                                addingItems[term] = new NodeItemTermLinksPair { Item = nodeItem, Links = linksToAnotherRecords };
                                continue;
                            }
                        }

                        //элементы в l01, которые надо как бы удалить остаются на месте, просто в лидере ifp записи проставляется 0 ссылок
                        //сами элементы не удаляются 
                        //leafNode.Items.Remove(nodeItem);                  
                        //removingItems[firstTermByKey] = nodeItem;
                        removingItems[term] = new NodeItemTermLinksPair { Item = nodeItem, Links = termLinks };
                    }
                }
            }

            return removingItems;
        }

        /// <summary>
        /// Обновление блоков дерева оглавления n01
        /// </summary>
        private void UpdateTree(NodeRecord[] nodes, bool newLevel, bool rebuild, bool padding)
        {
            var directIO = (IrbisDirectIO)_irbisIO;
            //номер первого блока в цепочке
            int firstNodeNumber = directIO.InvertedFile.GetFirstNodeNumber(nodes[0]);
            var items = new NodeItem[newLevel ? nodes.Length + 1 : nodes.Length];
            int itemOffset = 0;
            //в первом блоке нового уровня первый ключ создается всегда
            if (newLevel)
            {
                //int firstNodeNumber = _directIO.InvertedFile.GetFirstNodeNumber(nodes[0]);
                items[0] = new NodeItem
                {
                    Text = ((char)1).ToString(),
                    LowOffset = firstNodeNumber, /*первый ключ нового уровня ссылается на первый блок предыдущего уровня*/
                    NodeNumber = directIO.InvertedFile.ControlRecord.NodeBlockCount + 1
                };
                itemOffset = 1;
            }
            for (int i = 0; i < nodes.Length; i++)
            {
                var item = nodes[i].Items[0];
                items[itemOffset + i] = new NodeItem
                {
                    Text = item.Text,
                    NodeNumber = item.NodeNumber,
                    LowOffset = nodes[i].Leader.Number
                };
            }

            var addedNodes = new List<NodeRecord>();
            if (newLevel)
            {
                //создание нового уровня дерева
                var titleNode = new NodeRecord(false);
                titleNode.Leader.Number = directIO.InvertedFile.ControlRecord.NodeBlockCount + 1;
                titleNode.Leader.Previous = -1;
                titleNode.Leader.Next = -1;
#if TEXT_FIELDS
                titleNode.BeginEdit();
                titleNode.AddItems(items);
                titleNode.CommitEdit();
#else
                titleNode.Items.AddRange(items);
#endif
                directIO.InvertedFile.ControlRecord.NodeBlockCount++;
                directIO.InvertedFile.WriteControlRecord();
                var newNodes = directIO.InvertedFile.WriteNode(titleNode, rebuild, padding);
                if (newNodes != null && newNodes.Length > 0)
                    addedNodes.AddRange(newNodes);
                directIO.InvertedFile.WriteFirstNodeNumber(titleNode.Leader.Number);
            }
            else
            {
#if TEXT_FIELDS
                var editNodes = new List<NodeRecord>();
#endif
                firstNodeNumber = directIO.InvertedFile.GetUpperLevelFirstNodeNumber(firstNodeNumber, true);

                var nodeRecords = new Dictionary<int, NodeRecord>();
                //добавление терминов
                for (int i = 0; i < nodes.Length; i++)
                {
                    var item = items[i];
                    //удаление ключа в n01, если первый ключ в блоке нижнего уровня изменился
                    //if (nodes[i].RemovingParentKey != null)
                    //    SearchCheckNodeTerm(nodes[i].RemovingParentKey, nodes[i].Leader.Number, firstNodeNumber, true, nodeRecords, editNodes);

                    //null вернется, если термин найден и соответствует требуемому блоку
                    //var st = SearchCheckNodeTerm(item.Text, item.NodeNumber, firstNodeNumber, false, nodeRecords, editNodes);
                    var st = SearchCheckNodeTerm(item.Text, item.NodeNumber, firstNodeNumber, nodeRecords, editNodes);
                    if (st != null)
                    {
                        //начитаем блок N01
                        NodeRecord node = null;
                        if (!nodeRecords.TryGetValue(st.NodeNumber, out node))
                        {
                            node = directIO.InvertedFile.ReadNode(st.NodeNumber);
                            nodeRecords[st.NodeNumber] = node;
                        }

#if TEXT_FIELDS
                        if (node.BeginEdit())
                            editNodes.Add(node);
#endif
                        //добавим элементы
#if TEXT_FIELDS
                        node.AddItem(item);
#else
                    node.Items.Add(item);
#endif
                    }
                }
#if TEXT_FIELDS
                foreach (var node in editNodes)
                {
                    node.CommitEdit();
                }
                editNodes.Clear();
#endif
                var titleNodes = nodeRecords.Values.ToArray();
                foreach (var node in titleNodes)
                {
                    var newNodes = directIO.InvertedFile.WriteNode(node, rebuild, padding);
                    if (newNodes != null && newNodes.Length > 0)
                        addedNodes.AddRange(newNodes);
                }
                nodeRecords.Clear();
            }
            //запись новых ключей верхнего уровня дерева
            //если расширяется блок верхнего уровня, будет добавлен новый уровень
            if (addedNodes.Count > 0)
            {
                ////если только сменился первый ключ в блоке, новый уровень создавать не надо
                //if (addedNodes.Any(n => n.RemovingParentKey == null))
                //{
                firstNodeNumber = directIO.InvertedFile.GetFirstNodeNumber(addedNodes[0]);
                var upperLevelFirstNodeNumber = directIO.InvertedFile.GetUpperLevelFirstNodeNumber(firstNodeNumber, false);
                //если текущая цепочка на самом верхнем уровне, то создаем новый блок
                newLevel = upperLevelFirstNodeNumber <= 0;
                //}
                //else
                //    newLevel = false;

                UpdateTree(addedNodes.ToArray(), newLevel, rebuild, padding);
                addedNodes.Clear();
            }
        }

        protected override void CreateTmpDatabase()
        {
            var directIO = (IrbisDirectIO)_irbisIO;
            _tmpPath = Path.Combine(Path.GetDirectoryName(this.GetType().Assembly.Location), "TmpIndex");
            if (Directory.Exists(_tmpPath))
                Directory.Delete(_tmpPath, true);
            Directory.CreateDirectory(_tmpPath);

            var _tmpIrbisIO = _irbisIO;

            _irbisIO = new IrbisDirectIO(String.Format("{0}\\{1}.mst", _tmpPath, _tmpIrbisIO.Database), true);
            directIO.InvertedFile.Create();

            //актуализация словаря
            //добавить корневой блок
            CheckRootNode();
        }

        protected override void CopyTmpDatabase()
        {
            var directIO = (IrbisDirectIO)_irbisIO;
            //Пересборка индекса с помощью временных файлов
            var dummyTerms = new FstTermLink[0];

            var tmpDirectIO = (IrbisDirectIO)_irbisIO;
            _irbisIO = _tmpIrbisIO;
            _tmpIrbisIO = null;
            directIO.InvertedFile.Create();

            //_directIO.InvertedFile.Ifp.Seek(0, SeekOrigin.Begin);
            //_directIO.InvertedFile.Ifp.SetLength(0);
            //tmpDirectIO.InvertedFile.Ifp.Seek(0, SeekOrigin.Begin);
            //tmpDirectIO.InvertedFile.Ifp.CopyTo(_directIO.InvertedFile.Ifp);

            //_directIO.InvertedFile.N01.Seek(0, SeekOrigin.Begin);
            //_directIO.InvertedFile.N01.SetLength(0);
            //tmpDirectIO.InvertedFile.N01.Seek(0, SeekOrigin.Begin);
            //tmpDirectIO.InvertedFile.N01.CopyTo(_directIO.InvertedFile.N01);

            //_directIO.InvertedFile.L01.Seek(0, SeekOrigin.Begin);
            //_directIO.InvertedFile.L01.SetLength(0);
            //tmpDirectIO.InvertedFile.L01.Seek(0, SeekOrigin.Begin);
            //tmpDirectIO.InvertedFile.L01.CopyTo(_directIO.InvertedFile.L01);

            //запись по блокам l01 предпочтительнее, так как при сортировке l01 в n01 могут
            //появляться лишние ключи
            //их удаление не реализовано, так как могут образовываться пустые блоки.

            //актуализация словаря
            //добавить корневой блок
            CheckRootNode();

            var blockCount = tmpDirectIO.InvertedFile.ControlRecord.LeafBlockCount;
            NodeRecord leafNode = null;
            for (int i = 0; i < blockCount; i++)
            {
                int nodeNumber = i == 0 ? 1 : leafNode.Leader.Next;
                if (nodeNumber < 0)
                    break;
                leafNode = tmpDirectIO.InvertedFile.ReadLeaf(nodeNumber);
                //var addedTerms = leafNode.Items.Select(itm => new FstTermLink(0, new int[0], itm.Text, tmpDirectIO.InvertedFile.ReadIfpRecordFull(itm.FullOffset))).ToArray();
                var addedTerms = leafNode.Items.SelectMany(itm => tmpDirectIO.InvertedFile.ReadIfpRecordFull(itm.FullOffset).Select(l => new FstTermLink(itm.Text, l))).ToArray();
                UpdateTerms(addedTerms, dummyTerms, true);
            }
            tmpDirectIO.Dispose();
            Directory.Delete(_tmpPath, true);
            _tmpPath = null;
        }

    }
}
