/* InvertedFile.cs
 */

#region Using directives

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;

#endregion

namespace ManagedClient
{
    public class InvertedFile
        : IDisposable
    {
        #region Constants

        /// <summary>
        /// Длина записи N01/L01.
        /// </summary>
        public const int NodeLength = 2048;

        /// <summary>
        /// ibatrak максимальный размер термина
        /// </summary>
        public const int MaxTermSize = 255;

        /// <summary>
        /// ibatrak размер блока
        /// </summary>
        public const int BlockSize = 2050048;

        #endregion

        #region Properties

        /// <summary>
        /// ibatrak контрольная запись
        /// </summary>
        public InvertedFileControlRecord ControlRecord { get; private set; }

        public string FileName { get { return _fileName; } }

        public Stream Ifp { get { return _ifp; } }

        public Stream L01 { get { return _l01; } }

        public Stream N01 { get { return _n01; } }

        #endregion

        #region Construction

        //ibatrak новый конструктор с поддержкой записи
        public InvertedFile(string fileName, bool write)
        {
            _encoding = new UTF8Encoding(false, true);

            _fileName = fileName;

            _ifp = _OpenStream(fileName, write);
            _l01 = _OpenStream(Path.ChangeExtension(fileName, ".l01"), write);
            _n01 = _OpenStream(Path.ChangeExtension(fileName, ".n01"), write);
        }

        #endregion

        #region Private members

        private readonly string _fileName;

        private Stream _ifp;

        private Stream _l01;

        private Stream _n01;

        private readonly Encoding _encoding;

        private static Stream _OpenStream(string fileName, bool write)
        {
            if (!write)
            {
                return new FileStream
                    (
                        fileName,
                        FileMode.Open,
                        FileAccess.Read,
                        FileShare.ReadWrite,
                    //ibatrak минимальный размер буфера, для отключения буферизации
                        1
                    );
            }
            else
            {
                return new FileStream
                (
                    fileName,
                    FileMode.OpenOrCreate,
                    FileAccess.ReadWrite,
                    FileShare.Read,
                    //ibatrak минимальный размер буфера, для отключения буферизации
                    1
                );

            }
        }

        private long _NodeOffset(int nodeNumber)
        {
            //ibatrak здесь явное преобразование к более широкому типу, переполнения не будет
            //long result = unchecked((((long)nodeNumber) - 1) * NodeLength);
            long result = ((long)nodeNumber - 1) * NodeLength;
            return result;
        }

        private NodeRecord _ReadNode
            (
                bool isLeaf,
                Stream stream,
                long offset
            )
        {
            stream.Position = offset;
            var buffer = new byte[NodeLength];
            if (stream.Read(buffer, 0, buffer.Length) != buffer.Length)
                throw new IOException();

            NodeRecord result = new NodeRecord(isLeaf)
                {
                    _stream = stream,
                    //ibatrak метод вынесен отдельно
                    Leader = NodeLeader.Read(buffer, 0)
                    //Leader =
                    //    {
                    //        Number = stream.ReadInt32Network(),
                    //        Previous = stream.ReadInt32Network(),
                    //        Next = stream.ReadInt32Network(),
                    //        TermCount = stream.ReadInt16Network(),
                    //        FreeOffset = stream.ReadInt16Network()
                    //    }
                };

#if TEXT_FIELDS
            result.BeginEdit();
#endif

            for (int i = 0; i < result.Leader.TermCount; i++)
            {
                var bufferOffset = NodeLeader.Size + i * NodeItem.LeaderSize;
                NodeItem item = new NodeItem
                    {
                        //ibatrak номер блока в файле
                        NodeNumber = result.Leader.Number,
                        Length = buffer.ReadInt16Network(bufferOffset),
                        KeyOffset = buffer.ReadInt16Network(bufferOffset + 2),
                        LowOffset = buffer.ReadInt32Network(bufferOffset + 4),
                        HighOffset = buffer.ReadInt32Network(bufferOffset + 8)
                    };
#if TEXT_FIELDS
                result.AddItem(item);
#else
                result.Items.Add(item);
#endif
            }

            foreach (NodeItem item in result.Items)
            {
                string text = _encoding.GetString(buffer, item.KeyOffset, item.Length);
                item.Text = text;
            }

#if TEXT_FIELDS
            result.CommitEdit();
#endif
            return result;
        }

        /// <summary>
        /// ibatrak чтение поля low offset первого элемента - номер блока на уровень ниже
        /// </summary>
        private int _ReadFirstItemLowOffset
        (
            Stream stream,
            long offset
        )
        {
            stream.Position = offset + NodeLeader.Size + 4;
            var firstItemLowOffset = stream.ReadInt32Network();
            return firstItemLowOffset;
        }

        /// <summary>
        /// ibatrak чтение контрольной записи инвертного файла
        /// </summary>
        private void _ReadControlRecord()
        {
            _ifp.Position = 0;
            var buffer = new byte[InvertedFileControlRecord.RecordSize];
            if (_ifp.Read(buffer, 0, buffer.Length) != buffer.Length)
                throw new IOException();
            ControlRecord = new InvertedFileControlRecord
            {
                IfpOffset = buffer.ReadInt64Network(0),
                NodeBlockCount = buffer.ReadInt32Network(8),
                LeafBlockCount = buffer.ReadInt32Network(12),
                Reserv = buffer.ReadInt32Network(16)
            };
        }

        /// <summary>
        /// ibatrak инициализация контрольной записи инвертного файла
        /// </summary>
        private void _InitControlRecord()
        {
            if (_ifp.Length < InvertedFileControlRecord.RecordSize)
            {
                ControlRecord = new InvertedFileControlRecord
                {
                    IfpOffset = InvertedFileControlRecord.RecordSize,
                    NodeBlockCount = 0,
                    LeafBlockCount = 0,
                    Reserv = -1
                };
            }
            else
                _ReadControlRecord();
        }

        /// <summary>
        /// ibatrak запись контрольной записи инвертного файла
        /// </summary>
        private void _WriteControlRecord()
        {
            _ifp.Position = 0;
            var buffer = new byte[InvertedFileControlRecord.RecordSize];
            buffer.WriteInt64Network(ControlRecord.IfpOffset, 0);
            buffer.WriteInt32Network(ControlRecord.NodeBlockCount, 8);
            buffer.WriteInt32Network(ControlRecord.LeafBlockCount, 12);
            buffer.WriteInt32Network(ControlRecord.Reserv, 16);
            _ifp.Write(buffer, 0, buffer.Length);
            _ifp.Flush();
        }

        /// <summary>
        /// ibatrak для тестирования
        /// </summary>
        public void WriteControlRecord()
        {
            _WriteControlRecord();
        }

        /// <summary>
        /// ibatrak подготовка блока к записи, проверка размера
        /// </summary>
        private NodeRecord[] _CheckNodeSize(NodeRecord node, Stream stream, bool rebuld)
        {
            //при пересборке блоки должны заполняться на 90 %, при простом обновлении на 50
            double splitFactor = rebuld ? 0.9 : 0.5;
            //сортировка элементов в блоке
#if TEXT_FIELDS
            var items = new List<NodeItem>(node.Items);
#else
            var items = node.Items;

#endif
            items.Sort(new Comparison<NodeItem>((n1, n2) => String.Compare(n1.Text, n2.Text, StringComparison.OrdinalIgnoreCase)));

            int size = NodeLeader.Size + node.Items.Select(itm => NodeItem.LeaderSize + _encoding.GetByteCount(itm.Text)).DefaultIfEmpty().Sum();
            //если размер блока превышает максимальный, надо разбить блок на несколько
            //блоки делятся примерно пополам
            int newBlockSize = (int)Math.Ceiling((NodeLength - NodeLeader.Size) * splitFactor);
            List<NodeRecord> newNodes = null;
            //в Irbis_01.pas описано еще, что в блоке максимальное количество терминов - 255
            //проверять это смысла нет, так как при размере блока 2048 этого никогда не произойдет, просто не хватит места
            //int nodeCount = node.IsLeaf ? ControlRecord.LeafBlockCount : ControlRecord.NodeBlockCount;
            while (size > NodeLength)
            {
                if (newNodes == null)
                    newNodes = new List<NodeRecord>();
                int newNodeSize = 0;
                var newNode = new NodeRecord(node.IsLeaf);
#if TEXT_FIELDS
                newNode.BeginEdit();
#endif
                newNode._stream = node._stream;

                for (int i = items.Count - 1; i >= 0; i--)
                {
                    var item = items[i];
                    var termSize = _encoding.GetByteCount(item.Text);
                    if (termSize > MaxTermSize)
                        throw new Exception(String.Format("Размер термина {0} превышает максимально допустимый {1}, {2}",
                            termSize, MaxTermSize, item.Text));
                    var itemSize = NodeItem.LeaderSize + termSize;

#if TEXT_FIELDS
                    newNode.InsertItem(0, item);
#else
                    newNode.Items.Insert(0, item);
#endif
                    items.RemoveAt(i);
                    newNodeSize += itemSize;
                    size -= itemSize;
                    //блоки делятся при обновлении пополам, при пересборке блоки получают по 90 процентов заполнения
                    //если размер не симметричный, то первый блок получает большинство
                    if (newNodeSize >= newBlockSize || size <= newBlockSize)
                        break;
                }
                newNodes.Insert(0, newNode);
#if TEXT_FIELDS
                newNode.CommitEdit();
#endif
            }

#if TEXT_FIELDS
            bool nodeEdit = node.BeginEdit();
            node.Clear();
            node.AddItems(items);
            items.Clear();
            if (nodeEdit)
                node.CommitEdit();
#endif

            if (newNodes != null)
            {
                //установить номера блоков
                int nodeCount = node.IsLeaf ? ControlRecord.LeafBlockCount : ControlRecord.NodeBlockCount;
                for (int i = 0; i < newNodes.Count; i++)
                {
                    var newNode = newNodes[i];
                    newNode.Leader.Number = nodeCount + 1;
                    //в первом по списку новом блоке предыдущим блоком становится оригинальный блок
                    //остальные получают предыдущий по списку
                    newNode.Leader.Previous = i == 0 ? node.Leader.Number : nodeCount;
                    //все новые блоки, кроме последнего получают следующим следующий по списку блок
                    //последний в списке получает ссылку из оригинального блока
                    newNode.Leader.Next = i < newNodes.Count - 1 ? nodeCount + 2 : node.Leader.Next;
                    nodeCount++;
                }
                //оригинальный блок получает в качестве следующего первый в списке новых блок
                if (newNodes.Count > 0)
                {
                    //загрузить и обновить лидер блока, на который ссылается последний блок в списке
                    if (newNodes[newNodes.Count - 1].Leader.Next > 0)
                    {
                        node._stream.Position = _NodeOffset(newNodes[newNodes.Count - 1].Leader.Next);
                        var leader = NodeLeader.Read(node._stream);
                        leader.Previous = newNodes[newNodes.Count - 1].Leader.Number;
                        node._stream.Position = _NodeOffset(newNodes[newNodes.Count - 1].Leader.Next);
                        NodeLeader.Write(node._stream, leader);
                    }
                    node.Leader.Next = newNodes[0].Leader.Number;
                }

                var newNodeArr = newNodes.ToArray();
                newNodes.Clear();
                return newNodeArr;
            }
            return null;
        }

        /// <summary>
        /// ibatrak запись блока
        /// </summary>
        private void _WriteNode
        (
            NodeRecord node,
            Stream stream,
            long offset,
            bool padding
        )
        {
            if (stream.Seek(offset, SeekOrigin.Begin) != offset)
            {
                throw new IOException();
            }

            //подсчет смещения для записи значений элементов (пишутся в конец блока)
            short keyOffset = NodeLength;
            foreach (NodeItem item in node.Items)
            {
                item.Length = (short)_encoding.GetByteCount(item.Text);
                keyOffset -= item.Length;
                item.KeyOffset = keyOffset;
            }

            node.Leader.FreeOffset = keyOffset;

#if TEXT_FIELDS
            node.Leader.TermCount = node.Items.Length;
#else
            node.Leader.TermCount = node.Items.Count;
#endif

            var buffer = new byte[NodeLength];

            //запись лидера блока
            var bufferOffset = NodeLeader.Write(buffer, node.Leader, 0);

            //запись справочника элементов
            foreach (NodeItem item in node.Items)
            {
                var nodeItemOffset = bufferOffset;
                buffer.WriteInt16Network(item.Length, nodeItemOffset);
                buffer.WriteInt16Network(item.KeyOffset, nodeItemOffset + 2);
                buffer.WriteInt32Network(item.LowOffset, nodeItemOffset + 4);
                buffer.WriteInt32Network(item.HighOffset, nodeItemOffset + 8);
                bufferOffset += NodeItem.LeaderSize;
            }

            //запись значений элементов
            foreach (NodeItem item in node.Items)
            {
                byte[] textBuffer = _encoding.GetBytes(item.Text);
                Buffer.BlockCopy(textBuffer, 0, buffer, item.KeyOffset, textBuffer.Length);
            }

            //выравнивание размера файла
            if (padding && (offset + buffer.Length) > stream.Length)
            {
                long newSize = (long)Math.Ceiling((double)(offset + buffer.Length) / (double)BlockSize) * BlockSize;
                stream.SetLength(newSize);
            }

            stream.Write(buffer, 0, buffer.Length);
            stream.Flush();
        }

        #endregion

        #region Public methods

        public NodeRecord ReadNode(int number)
        {
            //ibatrak требуется установить настоящий номер в файле, так как может отличаться
            //для чтения номера первого блока сделан отдельный метод
            //return _ReadNode(false, _n01, _NodeOffset(number));
            var node = _ReadNode(false, _n01, _NodeOffset(number));
            if (node.Leader.Number != number)
            {
                node.Leader.Number = number;
                foreach (var item in node.Items)
                {
                    item.NodeNumber = number;
                }
            }
            return node;
        }

        public NodeRecord ReadLeaf(int number)
        {
            number = Math.Abs(number);
            return _ReadNode(true, _l01, _NodeOffset(number));
        }

        /// <summary>
        /// ibatrak чтение номера блока на следующем уровне
        /// </summary>
        public int ReadFirstItemLowOffset(int number)
        {
            number = Math.Abs(number);
            return _ReadFirstItemLowOffset(_n01, _NodeOffset(number));
        }

        /// <summary>
        /// ibatrak чтение номера первого блока
        /// </summary>
        public int ReadFirstNodeNumber()
        {
            if (_n01.Length == 0)
                return 1;
            if (_n01.Seek(0, SeekOrigin.Begin) != 0)
                throw new IOException();
            int number = _n01.ReadInt32Network();
            return number;
        }

        /// <summary>
        /// ibatrak запись номера первого блока
        /// </summary>
        public void WriteFirstNodeNumber(int number)
        {
            if (_n01.Seek(0, SeekOrigin.Begin) != 0)
                throw new IOException();
            _n01.WriteInt32Network(number);
            _n01.Flush();
        }

        /// <summary>
        /// ibatrak поиск первого блока в цепочке
        /// </summary>
        public int GetFirstNodeNumber(NodeRecord node)
        {
            if (node.IsLeaf)
                throw new InvalidOperationException("Поиск первого номера блока в цепочке возможен только для N01");
            //блоки, которые ссылаются на листья идут от первого номера
#if TEXT_FIELDS
            if (node.Items.Length > 0 && node.Items[0].RefersToLeaf)
#else
            if (node.Items.Count > 0 && node.Items[0].RefersToLeaf)
#endif
                return 1;
            var leader = node.Leader;
            while (leader.Previous > 0)
            {
                _n01.Position = _NodeOffset(leader.Previous);
                _n01.Flush();
                leader = NodeLeader.Read(_n01);
            }
            return leader.Number;
        }

        /// <summary>
        /// ibatrak поиск первого по цепочке блока на один уровень выше
        /// </summary>
        public int GetUpperLevelFirstNodeNumber(int currentLevelFirstNodeNumber, bool throwIfNotFound)
        {
            //if (node.IsLeaf)
            //    throw new InvalidOperationException("Поиск первого номера блока в цепочке возможен только для N01");

            //var currentLevelFirstNodeNumber = GetFirstNodeNumber(node);

            var firstNodeNumber = ReadFirstNodeNumber();

            if (firstNodeNumber == currentLevelFirstNodeNumber)
            {
                if (throwIfNotFound)
                    throw new InvalidOperationException("Указанный блок находится на верхнем уровне");
                else
                    return 0;
            }

            var offset = _NodeOffset(firstNodeNumber);
            var upperLevelFirstNodeNumber = firstNodeNumber;
            //обход дерева вглубь, поиск блока на 1 уровень выше нужного
            while (true)
            {
                //_n01.Position = offset + NodeLeader.Size + 4;
                //var firstItemLowOffset = _n01.ReadInt32Network();
                var firstItemLowOffset = _ReadFirstItemLowOffset(_n01, offset);
                if (firstItemLowOffset < 0)
                    throw new InvalidOperationException("Ключи блоков дерева оглавления не могут ссылаться на листья");
                if (currentLevelFirstNodeNumber == firstItemLowOffset)
                    return upperLevelFirstNodeNumber;
                if (firstItemLowOffset == 1)
                    break;
                offset = _NodeOffset(firstItemLowOffset);
                upperLevelFirstNodeNumber = firstItemLowOffset;
            }

            throw new InvalidOperationException("Не удалось найти номер первого блока на один уровень выше");
        }

        /// <summary>
        /// ibatraka тестовый метод для проверки содержимого инвертного файла
        /// </summary>
        public void CheckData()
        {
            var first = ReadFirstNodeNumber();
            var node = ReadNode(1);
            var fNode = 1;
            while (true)
            {
                for (int i = 0; i < node.Items.Length; i++)
                {
                    if (node.Items[i].RefersToLeaf)
                    {
                        if (Math.Abs(node.Items[i].LowOffset) > 1)
                        {
                            var leaf = ReadLeaf(node.Items[i].LowOffset);
                            if (leaf.Items[0].Text != node.Items[i].Text)
                                throw new Exception("Несоответствие");
                        }
                    }
                    else
                    {
                        var subNode = ReadNode(node.Items[i].LowOffset);
                        if (subNode.Items[0].Text != node.Items[i].Text)
                            throw new Exception("Несоответствие");
                    }
                }
                if (node.Leader.Next > 0)
                    node = ReadNode(node.Leader.Next);
                else if (fNode != first)
                {
                    fNode = GetUpperLevelFirstNodeNumber(fNode, false);
                    node = ReadNode(fNode);
                }
                else
                    break;
            }
        }


        /// <summary>
        /// ibatrak запись блока n01
        /// </summary>
        public NodeRecord[] WriteNode(NodeRecord node, bool rebuild, bool padding)
        {
            //контрольная запись создается при первой записи в инвертный файл
            if (ControlRecord == null)
                _InitControlRecord();
            if (_n01.Length == 0)
                ControlRecord.NodeBlockCount = 1;
            var newNodes = _CheckNodeSize(node, _n01, rebuild);
            if (newNodes != null && newNodes.Length > 0)
                ControlRecord.NodeBlockCount += newNodes.Length;
            //если есть новые блоки, надо обновить контрольную запись
            if (_n01.Length == 0 || (newNodes != null && newNodes.Length > 0))
                _WriteControlRecord();
            //для первой записи надо запомнить номер первого блока, и обновить потом, если отличается
            int firstNodeNumber = 0;
            if (node.Leader.Number == 1)
            {
                firstNodeNumber = ReadFirstNodeNumber();
                if (firstNodeNumber <= 0)
                    firstNodeNumber = node.Leader.Number;
            }
            _WriteNode(node, _n01, _NodeOffset(node.Leader.Number), padding);
            if (node.Leader.Number == 1 && firstNodeNumber != node.Leader.Number)
                WriteFirstNodeNumber(firstNodeNumber);

            //запись разделенных блоков при превышении максимально допустимого размера блока
            if (newNodes != null && newNodes.Length > 0)
            {
                foreach (var newNode in newNodes)
                {
                    _WriteNode(newNode, _n01, _NodeOffset(newNode.Leader.Number), padding);
                }
            }
            //если первый ключ сменился, то новый ключ также требуется добавить
            //это отмечается в методе SearchCheckAndRemoveNodeTerm, там где удаляется ключ
            //if (node.RemovingParentKey != null)
            //{
            //    if (newNodes == null || newNodes.Length == 0)
            //        newNodes = new NodeRecord[] { node };
            //    else
            //    {
            //        Array.Resize(ref newNodes, newNodes.Length + 1);
            //        newNodes[newNodes.Length - 1] = node;
            //    }
            //}
            return newNodes;
        }

        /// <summary>
        /// ibatrak запись блока l01
        /// </summary>
        public NodeRecord[] WriteLeaf(NodeRecord node, bool rebuild, bool padding)
        {
            //контрольная запись создается при первой записи в инвертный файл
            if (ControlRecord == null)
                _InitControlRecord();
            if (_l01.Length == 0)
                ControlRecord.LeafBlockCount = 1;
            //var firstItem = node.Items.Length > 0 ? node.Items[0] : null;
            var newNodes = _CheckNodeSize(node, _l01, rebuild);
            if (newNodes != null && newNodes.Length > 0)
                ControlRecord.LeafBlockCount += newNodes.Length;
            //если есть новые блоки, надо обновить контрольную запись
            if (_l01.Length == 0 || (newNodes != null && newNodes.Length > 0))
                _WriteControlRecord();
            _WriteNode(node, _l01, _NodeOffset(node.Leader.Number), padding);

            //запись разделенных блоков при превышении максимально допустимого размера блока
            if (newNodes != null && newNodes.Length > 0)
            {
                foreach (var newNode in newNodes)
                {
                    _WriteNode(newNode, _l01, _NodeOffset(newNode.Leader.Number), padding);
                }
            }
            //если первый ключ сменился, то новый ключ также требуется добавить
            //если блок стоит дальше первого, первый блок не имеет отдельных ключей
            //if (firstItem != null && firstItem.NodeNumber > 1 && node.Items[0].Text != firstItem.Text)
            //{
            //    node.RemovingParentKey = firstItem.Text;
            //    if (newNodes == null || newNodes.Length == 0)
            //        newNodes = new NodeRecord[] { node };
            //    else
            //    {
            //        Array.Resize(ref newNodes, newNodes.Length + 1);
            //        newNodes[newNodes.Length - 1] = node;
            //    }
            //}
            return newNodes;
        }

        public NodeRecord ReadNext(NodeRecord record)
        {
            int number = record.Leader.Next;

            if (number < 0)
            {
                return null;
            }

            return _ReadNode(record.IsLeaf, record._stream, _NodeOffset(number));
        }

        public NodeRecord ReadPrevious(NodeRecord record)
        {
            int number = record.Leader.Previous;
            if (number < 0)
            {
                return null;
            }

            return _ReadNode(record.IsLeaf, record._stream, _NodeOffset(number));
        }

        public IfpRecord ReadIfpRecord(long offset)
        {
            IfpRecord result = IfpRecord.Read(Ifp, offset);
            return result;
        }

        /// <summary>
        /// ibatrak запись Ifp
        /// </summary>
        public void WriteIfpRecord(NodeItem item, TermLink[] links, bool padding)
        {
            //контрольная запись создается при первой записи в инвертный файл
            if (ControlRecord == null)
                _InitControlRecord();
            if (_ifp.Length == 0)
                _WriteControlRecord();
            if (links != null)
            {
                int size = IfpRecord.Write(_ifp, item, links, ControlRecord.IfpOffset, padding);
                //int size = IfpRecord.WriteNew(_ifp, terms, item.FullOffset, ControlRecord.IfpOffset, padding);
                //если была создана новая запись, обновить контрольную запись
                if (size > 0)
                {
                    ControlRecord.IfpOffset += size;
                    _WriteControlRecord();
                }
            }
            else //при удалении ключа просто обнулить количество ссылок
                IfpRecord.ClearItems(_ifp, item.FullOffset);
        }

        /// <summary>
        /// ibatrak инициализация инвертного файла
        /// </summary>
        public void Create()
        {
            _n01.Seek(0, SeekOrigin.Begin);
            _n01.SetLength(0);
            _l01.Seek(0, SeekOrigin.Begin);
            _l01.SetLength(0);

            _ifp.Seek(0, SeekOrigin.Begin);
            _ifp.SetLength(0);
        }

        /// <summary>
        /// ibatrak создание корневых блоков в n01 и l01
        /// </summary>
        public void CreateRootNode(bool padding)
        {
            if (_n01.Length > 0 || _l01.Length > 0)
                throw new IOException("База данных не пустая");
            //создадим корневой блок в n01
            var root = new NodeRecord();
            var rootItem = new NodeItem { Text = ((char)1).ToString(), LowOffset = -1, NodeNumber = 1 };
            root.Leader.Number = 1;
            root.Leader.Previous = -1;
            root.Leader.Next = -1;
#if TEXT_FIELDS
            root.BeginEdit();
            root.AddItem(rootItem);
            root.CommitEdit();
#else
            root.Items.Add(rootItem);
#endif
            WriteNode(root, false, padding);

            //создадим первый блок в l01
            var firstLeaf = new NodeRecord();
            firstLeaf.Leader.Number = 1;
            firstLeaf.Leader.Previous = -1;
            firstLeaf.Leader.Next = -1;
            WriteLeaf(firstLeaf, false, padding);
        }

        public TermLink[] SearchExact(string key)
        {
            return SearchExact(key, 0, 0);
        }

        public TermLink[] SearchExact(string key, int first, int limit)
        {
            if (string.IsNullOrEmpty(key)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
            {
                return new TermLink[0];
            }

            key = key.ToUpperInvariant();

            //ibatrak ирбис читает номер, потом отдельно блоки
            //NodeRecord firstNode = ReadNode(1);
            //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord rootNode = ReadNode(firstNodeNumber);
            NodeRecord currentNode = rootNode;

            NodeItem goodItem = null;
            while (true)
            {
                //ibatrak если база пустая, на выход
                //if (currentNode.Items.Count == 0)
                //    return new TermLink[0];
                bool found = false;
                bool beyond = false;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, key);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;

                    if ((compareResult == 0)
                        && currentNode.IsLeaf)
                    {
                        goto FOUND;
                    }

                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        //ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
                        if (currentNode.IsLeaf)
                            return null;

                        currentNode = goodItem.RefersToLeaf
                            ? ReadLeaf(goodItem.LowOffset)
                            : ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    //ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
                    if (currentNode.IsLeaf)
                        return null;

                    currentNode = goodItem.RefersToLeaf
                        ? ReadLeaf(goodItem.LowOffset)
                        : ReadNode(goodItem.LowOffset);
                }
                //Console.WriteLine(currentNode);
            }

        FOUND:
            if (goodItem != null)
            {
                //ibatrak записи могут иметь ссылки на следующие
                //IfpRecord ifp = ReadIfpRecord(goodItem.FullOffset);
                //return ifp.Links.ToArray();

                return ReadIfpRecord(goodItem.FullOffset, first, limit);

                //ibatrak до сюда

            }

            return new TermLink[0];
        }

        //реализация рабочая, но бесполезная, так как требуется то, что реализовано в SearchRange
        ///// <summary>
        ///// ibatrak поиск по диапазону терминов
        ///// </summary>
        //public TermLink[] SearchExact(string keyA, string keyB)
        //{
        //    //сначала ищется первый термин по строгому соответствию ключу, как только он найден
        //    //идет цикл по терминам пока найденный термин не сменит имя индекса или не перевалит за 
        //    //границу второго термина
        //    if (string.IsNullOrEmpty(keyA) || string.IsNullOrEmpty(keyB)
        //        /*ibatrak если база пустая, на выход*/
        //        || _n01.Length == 0)
        //    {
        //        return new TermLink[0];
        //    }

        //    keyA = keyA.ToUpperInvariant();
        //    keyB = keyB.ToUpperInvariant();
        //    //предполагаем, что оба термина имеют общий индекс
        //    var indexName = keyA.Substring(0, keyA.IndexOf("=") + 1);
        //    if (!keyB.StartsWith(indexName))
        //        throw new ArgumentException(String.Format("Термины ссылаются на разные индексы: {0} {1}", keyA, keyB));

        //    //ibatrak ирбис читает номер, потом отдельно блоки
        //    //NodeRecord firstNode = ReadNode(1);
        //    //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
        //    int firstNodeNumber = ReadFirstNodeNumber();
        //    NodeRecord rootNode = ReadNode(firstNodeNumber);
        //    NodeRecord currentNode = rootNode;

        //    NodeItem goodItem = null;

        //    List<TermLink> result = new List<TermLink>();
        //    bool firstMatched = false;

        //    while (true)
        //    {
        //        //ibatrak если база пустая, на выход
        //        //if (currentNode.Items.Count == 0)
        //        //    return new TermLink[0];
        //        bool found = false;
        //        bool beyond = false;

        //        foreach (NodeItem item in currentNode.Items)
        //        {
        //            int compareResultA = string.CompareOrdinal(item.Text, keyA);
        //            int compareResultB = string.CompareOrdinal(item.Text, keyB);

        //            //if (compareResultA > 0)
        //            //{
        //            //    beyond = true;
        //            //    break;
        //            //}

        //            //если первый термин еще не найден проверяем результат сравнения и переходим к следующему термину
        //            //по необходимости
        //            if (!firstMatched)
        //            {
        //                if (compareResultA > 0)
        //                {
        //                    beyond = true;
        //                    break;
        //                }
        //            }
        //            else
        //            {
        //                //если сменился индекс или вышли за границу 
        //                //терминов, которые имеют значение (длиннее ключа),
        //                //возвращаем результат
        //                if (!item.Text.StartsWith(indexName) ||
        //                    (keyA.Length > indexName.Length && compareResultA < 0) ||
        //                    (keyB.Length > indexName.Length && compareResultB > 0))
        //                {
        //                    //beyond = true;
        //                    //break;

        //                    var resultArr = result.Distinct().ToArray();
        //                    result.Clear();
        //                    return resultArr;
        //                }
        //            }

        //            //если выскочили за правую границу терминов, читаем следующий блок
        //            //if (compareResultB > 0)
        //            //{
        //            //    beyond = true;
        //            //    break;
        //            //}

        //            goodItem = item;
        //            found = true;

        //            //если нашли первый термин, запомним это
        //            if ((compareResultA == 0)
        //               && currentNode.IsLeaf)
        //            {
        //                //goto FOUND;
        //                firstMatched = true;
        //            }

        //            if (item.Text.StartsWith(indexName) &&
        //                (keyA.Length > indexName.Length ? compareResultA >= 0 : true) &&
        //                (keyB.Length > indexName.Length ? compareResultB <= 0 : true) &&
        //                    currentNode.IsLeaf)
        //            {
        //                //goto FOUND;

        //                //ibatrak записи могут иметь ссылки на следующие
        //                //IfpRecord ifp = ReadIfpRecord(goodItem.FullOffset);
        //                //return ifp.Links.ToArray();

        //                ReadIfpRecordFull(result, goodItem.FullOffset);

        //            }

        //        }
        //        if (goodItem == null)
        //        {
        //            break;
        //        }
        //        if (found)
        //        {
        //            if (beyond || (currentNode.Leader.Next == -1))
        //            {
        //                //ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
        //                if (currentNode.IsLeaf)
        //                    return new TermLink[0];

        //                currentNode = goodItem.RefersToLeaf
        //                    ? ReadLeaf(goodItem.LowOffset)
        //                    : ReadNode(goodItem.LowOffset);
        //            }
        //            else
        //            {
        //                currentNode = ReadNext(currentNode);
        //            }
        //        }
        //        else
        //        {
        //            //ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
        //            if (currentNode.IsLeaf)
        //                return new TermLink[0];

        //            currentNode = goodItem.RefersToLeaf
        //                ? ReadLeaf(goodItem.LowOffset)
        //                : ReadNode(goodItem.LowOffset);
        //        }
        //        //Console.WriteLine(currentNode);
        //    }

        //    return new TermLink[0];
        //}

        /// <summary>
        /// ibatrak поиск по диапазону терминов
        /// </summary>
        public TermLink[] SearchRange(string keyA, string keyB)
        {
            //похоже на метод SearchTermsFrom, только поиск в одном направлении и до достижения термина Б
            if (string.IsNullOrEmpty(keyA) || string.IsNullOrEmpty(keyB)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
            {
                return new TermLink[0];
            }
            List<TermLink> result = new List<TermLink>();

            keyA = keyA.ToUpperInvariant();
            keyB = keyB.ToUpperInvariant();
            //предполагаем, что оба термина имеют общий индекс
            var indexName = keyA.Substring(0, keyA.IndexOf("=") + 1);
            if (!keyB.StartsWith(indexName))
                throw new ArgumentException(String.Format("Термины ссылаются на разные индексы: {0} {1}", keyA, keyB));

            //ibatrak ирбис читает номер, потом отдельно блоки
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord currentNode = ReadNode(firstNodeNumber);

            NodeItem goodItem = null;
            bool firstItemFound = false;
            while (true)
            {
                bool found = false;
                bool beyond = false;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, keyA);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;
                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        if (goodItem.RefersToLeaf)
                        {
                            goto FOUND;
                        }
                        currentNode = ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    if (goodItem.RefersToLeaf)
                    {
                        goto FOUND;
                    }
                    currentNode = ReadNode(goodItem.LowOffset);
                }
            }

        FOUND:
            if (goodItem != null)
            {
                currentNode = ReadLeaf(goodItem.LowOffset);
                while (true)
                {
#if TEXT_FIELDS
                    for (int i = 0; i < currentNode.Items.Length; i++)
#else
                    for (int i = 0; i < currentNode.Items.Count; i++)
#endif
                    {
                        NodeItem item = currentNode.Items[i];

                        int compareResult = -1;
                        if (!firstItemFound && item.Text.StartsWith(indexName))
                            compareResult = string.CompareOrdinal(item.Text, keyA);
                        //первый результат может не содержать искомый текст
                        if (firstItemFound || compareResult >= 0)
                        {
                            if ((firstItemFound && !item.Text.StartsWith(indexName)) ||
                                    (keyA.Length > indexName.Length && string.CompareOrdinal(item.Text, keyA) < 0) ||
                                    (keyB.Length > indexName.Length && string.CompareOrdinal(item.Text, keyB) > 0))
                                goto DONE;

                            if (!firstItemFound)
                                firstItemFound = true;

                            IfpRecord ifp = IfpRecord.ReadLeader(Ifp, item.FullOffset);
                            //выводим только термины, где есть ссылки
                            if (ifp.TotalLinkCount > 0)
                            {
                                ReadIfpRecordFull(result, item.FullOffset);
                            }
                        }
                    }
                    if (currentNode.Leader.Next > 0)
                        currentNode = ReadNext(currentNode);
                    else
                        break;

                }

            }

        DONE:
            var terms = result.ToArray();
            result.Clear();
            return terms;
        }


        /// <summary>
        /// ibatrak поиск ссылок по mfn записи
        /// </summary>
        public Dictionary<int, Dictionary<string, TermLink[]>> SearchByMfn(int mfnFrom, int mfnTo)
        {
            var d = new Dictionary<int, Dictionary<string, TermLink[]>>();
            NodeRecord currentNode = ReadLeaf(1);

            Action<NodeItem> readLinks = (itm) =>
                {
                    IfpRecord ifp = null;
                    var offset = itm.FullOffset;
                    while (offset > 0)
                    {
                        ifp = ReadIfpRecord(offset);
                        foreach (var g in ifp.Links.Where(l => l.Mfn >= mfnFrom && l.Mfn <= mfnTo).GroupBy(l => l.Mfn))
                        {
                            Dictionary<string, TermLink[]> dict = null;
                            if (!d.TryGetValue(g.Key, out dict))
                            {
                                dict = new Dictionary<string, TermLink[]>();
                                d.Add(g.Key, dict);
                            }
                            TermLink[] links = null;
                            if (!dict.TryGetValue(itm.Text, out links))
                                dict.Add(itm.Text, g.ToArray());
                            else
                                dict[itm.Text] = links.Concat(g).ToArray();
                        }
                        if (ifp.FullOffset > 0)
                            offset = ifp.FullOffset;
                        else
                            offset = 0;
                    }
                };

            Action<NodeRecord> readNode = null;

            readNode = (n) =>
                {
                    if (n == null)
                        return;
                    foreach (NodeItem item in n.Items)
                    {
                        readLinks(item);
                    }
                };


            while (true)
            {
                //ibatrak если база пустая, на выход
#if TEXT_FIELDS
                if (currentNode == null || currentNode.Items.Length == 0)
#else
                if (currentNode == null || currentNode.Items.Count == 0)
#endif
                    break;

                readNode(currentNode);
                currentNode = ReadNext(currentNode);
            }

            return d;
        }

        ///// <summary>
        ///// ibatrak поиск терминов  (без чтения ссылок)
        ///// </summary>
        //public SearchTermInfo SearchTermExact(string key)
        //{
        //    if (string.IsNullOrEmpty(key))
        //    {
        //        return null;
        //    }

        //    key = key.ToUpperInvariant();

        //    NodeRecord firstNode = ReadNode(1);
        //    NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
        //    NodeRecord currentNode = rootNode;

        //    NodeItem goodItem = null;
        //    while (true)
        //    {
        //        //ibatrak если база пустая, на выход
        //        if (currentNode.Items.Count == 0)
        //            return null;
        //        bool found = false;
        //        bool beyond = false;

        //        foreach (NodeItem item in currentNode.Items)
        //        {
        //            int compareResult = string.CompareOrdinal(item.Text, key);
        //            if (compareResult > 0)
        //            {
        //                beyond = true;
        //                break;
        //            }

        //            goodItem = item;
        //            found = true;

        //            if ((compareResult == 0)
        //                && currentNode.IsLeaf)
        //            {
        //                goto FOUND;
        //            }

        //        }
        //        if (goodItem == null)
        //        {
        //            break;
        //        }
        //        if (found)
        //        {
        //            if (beyond || (currentNode.Leader.Next == -1))
        //            {
        //                currentNode = goodItem.RefersToLeaf
        //                    ? ReadLeaf(goodItem.LowOffset)
        //                    : ReadNode(goodItem.LowOffset);
        //            }
        //            else
        //            {
        //                currentNode = ReadNext(currentNode);
        //            }
        //        }
        //        else
        //        {
        //            currentNode = goodItem.RefersToLeaf
        //                ? ReadLeaf(goodItem.LowOffset)
        //                : ReadNode(goodItem.LowOffset);
        //        }
        //        //Console.WriteLine(currentNode);
        //    }

        //FOUND:
        //    if (goodItem != null)
        //    {
        //        IfpRecord ifp = IfpRecord.ReadLeader(Ifp, goodItem.FullOffset);
        //        return new SearchTermInfo { Text = goodItem.Text, Count = ifp.TotalLinkCount };
        //    }
        //    return null;
        //}

        /// <summary>
        /// ibatrak чтение ссылок термина
        /// </summary>
        public TermLink[] GetTermLinks(SearchTermInfo term, int first, int limit)
        {
            if (term.FullOffset > 0L)
                return ReadIfpRecord(term.FullOffset, first, limit);
            return null;
        }

        public TermLink[] SearchStart(string key)
        {
            return SearchStart(key, 0);
        }

        public TermLink[] SearchStart(string key, int limit)
        {
            //ibatrak список инициализируем после возможного выхода из метода
            //List<TermLink> result = new List<TermLink>();

            if (string.IsNullOrEmpty(key)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
            {
                return new TermLink[0];
            }

            //HashSet для отбрасывания дублирующих элементов и контроля количества
            //List<TermLink> result = new List<TermLink>();
            HashSet<TermLink> result = new HashSet<TermLink>();

            key = key.ToUpperInvariant();

            //ibatrak ирбис читает номер, потом отдельно блоки
            //NodeRecord firstNode = ReadNode(1);
            //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord rootNode = ReadNode(firstNodeNumber);
            NodeRecord currentNode = rootNode;

            NodeItem goodItem = null;
            while (true)
            {
                //ibatrak если база пустая, на выход
                //if (currentNode.Items.Count == 0)
                //    goto DONE;
                bool found = false;
                bool beyond = false;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, key);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;
                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        if (goodItem.RefersToLeaf)
                        {
                            goto FOUND;
                        }
                        currentNode = ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    if (goodItem.RefersToLeaf)
                    {
                        goto FOUND;
                    }
                    currentNode = ReadNode(goodItem.LowOffset);
                }
                //Console.WriteLine(currentNode);
            }

        FOUND:
            if (goodItem != null)
            {
                currentNode = ReadLeaf(goodItem.LowOffset);
                while (true)
                {
                    foreach (NodeItem item in currentNode.Items)
                    {
                        int compareResult = string.CompareOrdinal(item.Text, key);
                        if (compareResult >= 0)
                        {
                            bool starts = item.Text.StartsWith(key);
                            if ((compareResult > 0) && !starts)
                            {
                                goto DONE;
                            }
                            if (starts)
                            {
                                //ibatrak записи могут иметь ссылки на следующие
                                //IfpRecord ifp = ReadIfpRecord(offset);
                                //result.AddRange(ifp.Links);

                                ReadIfpRecord(result, item.FullOffset, 0, limit);
                                //если задано ограничение, выходим
                                if (limit > 0 && result.Count >= limit)
                                    goto DONE;
                                //ibatrak до сюда
                            }
                        }
                    }
                    if (currentNode.Leader.Next > 0)
                        currentNode = ReadNext(currentNode);
                    else //ibatrak не было выхода из цикла, добавил
                        break;
                }

            }

        DONE:
            var resultArr = result.ToArray();
            result.Clear();
            return resultArr;
            //return result
            //    .Distinct()
            //    .ToArray();
        }

        /// <summary>
        /// ibatrak чтение ссылок по цепочке из записей ifp
        /// </summary>
        public TermLink[] ReadIfpRecord(long offset, int first, int limit)
        {
            var list = new HashSet<TermLink>();
            ReadIfpRecord(list, offset, first, limit);
            //var links = list.Distinct().ToArray();
            var links = list.ToArray();
            list.Clear();
            return links;
        }

        /// <summary>
        /// ibatrak чтение всех ссылок по цепочке из записей ifp
        /// </summary>
        public TermLink[] ReadIfpRecordFull(long offset)
        {
            return ReadIfpRecord(offset, 0, 0);
        }

        /// <summary>
        /// ibatrak чтение ссылок по цепочке из записей ifp
        /// </summary>
        private void ReadIfpRecordFull(ICollection<TermLink> result, long offset)
        {
            ReadIfpRecord(result, offset, 0, 0);
        }

        /// <summary>
        /// ibatrak чтение ссылок по цепочке из записей ifp
        /// </summary>
        private void ReadIfpRecord(ICollection<TermLink> result, long offset, int first, int limit)
        {
            IfpRecord ifp = null;
            while (offset > 0)
            {
                ifp = ReadIfpRecord(offset);
                var index = first > 0 ? first - 1 : 0;
                var length = limit == 0 ? ifp.Links.Count - index : Math.Min(ifp.Links.Count - index, limit);
                for (int i = 0; i < length; i++)
                {
                    result.Add(ifp.Links[i + index]);
                }
                if (limit > 0 && result.Count >= limit)
                    break;
                if (ifp.FullOffset > 0)
                    offset = ifp.FullOffset;
                else
                    offset = 0;
            }
        }

        /// <summary>
        /// ibatrak поиск терминов (без чтения ссылок)
        /// </summary>
        public SearchTermInfo[] SearchTermsStart(string key, int limit)
        {
            if (string.IsNullOrEmpty(key)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
            {
                return new SearchTermInfo[0];
            }
            List<SearchTermInfo> result = new List<SearchTermInfo>();

            key = key.ToUpperInvariant();

            //ibatrak ирбис читает номер, потом отдельно блоки
            //NodeRecord firstNode = ReadNode(1);
            //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord rootNode = ReadNode(firstNodeNumber);

            NodeRecord currentNode = rootNode;

            NodeItem goodItem = null;
            while (true)
            {
                //ibatrak если база пустая, на выход
                //if (currentNode.Items.Count == 0)
                //    goto DONE;
                bool found = false;
                bool beyond = false;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, key);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;
                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        if (goodItem.RefersToLeaf)
                        {
                            goto FOUND;
                        }
                        currentNode = ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    if (goodItem.RefersToLeaf)
                    {
                        goto FOUND;
                    }
                    currentNode = ReadNode(goodItem.LowOffset);
                }
                //Console.WriteLine(currentNode);
            }

        FOUND:
            if (goodItem != null)
            {
                currentNode = ReadLeaf(goodItem.LowOffset);
                while (true)
                {
                    foreach (NodeItem item in currentNode.Items)
                    {
                        int compareResult = string.CompareOrdinal(item.Text, key);
                        if (compareResult >= 0)
                        {
                            bool starts = item.Text.StartsWith(key);
                            if ((compareResult > 0) && !starts)
                            {
                                goto DONE;
                            }
                            if (starts)
                            {
                                IfpRecord ifp = IfpRecord.ReadLeader(Ifp, item.FullOffset);
                                //выводим только термины, где есть ссылки
                                if (ifp.TotalLinkCount > 0)
                                {
                                    result.Add(new SearchTermInfo
                                    {
                                        Text = item.Text,
                                        Count = ifp.TotalLinkCount,
                                        NodeNumber = goodItem.NodeNumber,
                                        LeafNodeNumber = item.NodeNumber,
                                        FullOffset = item.FullOffset
                                    });
                                    //если задано ограничение, выходим
                                    if (limit > 0 && result.Count >= limit)
                                        goto DONE;
                                }
                            }
                        }
                    }
                    if (currentNode.Leader.Next > 0)
                        currentNode = ReadNext(currentNode);
                    else
                        break;
                }
            }

        DONE:
            var terms = result.ToArray();
            result.Clear();
            return terms;
        }

        /// <summary>
        /// ibatrak поиск терминов начиная с указанного (без чтения ссылок)
        /// </summary>
        public SearchTermInfo[] SearchTermsFrom(string key, bool searchBack, int limit)
        {
            if (string.IsNullOrEmpty(key)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
            {
                return new SearchTermInfo[0];
            }
            List<SearchTermInfo> result = new List<SearchTermInfo>();

            key = key.ToUpperInvariant();

            //ibatrak ирбис читает номер, потом отдельно блоки
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord rootNode = ReadNode(firstNodeNumber);

            NodeRecord currentNode = rootNode;

            NodeItem goodItem = null;
            bool firstItemFound = false;
            while (true)
            {
                bool found = false;
                bool beyond = false;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, key);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;
                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        if (goodItem.RefersToLeaf)
                        {
                            goto FOUND;
                        }
                        currentNode = ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    if (goodItem.RefersToLeaf)
                    {
                        goto FOUND;
                    }
                    currentNode = ReadNode(goodItem.LowOffset);
                }
            }

        FOUND:
            if (goodItem != null)
            {
                currentNode = ReadLeaf(goodItem.LowOffset);
                bool goBack = false;
                while (true)
                {
#if TEXT_FIELDS
                    for (int i = goBack ? currentNode.Items.Length - 1 : 0; goBack ? i >= 0 : i < currentNode.Items.Length; i += goBack ? -1 : 1)
#else
                    for (int i = goBack ? currentNode.Items.Count - 1 : 0; goBack ? i >= 0 : i < currentNode.Items.Count; i += goBack ? -1 : 1)
#endif
                    {
                        NodeItem item = currentNode.Items[i];
                        int compareResult = 0;
                        if (!firstItemFound)
                            compareResult = string.CompareOrdinal(item.Text, key);
                        //первый результат может не содержать искомый текст
                        if (firstItemFound || compareResult >= 0)
                        {
                            if (!firstItemFound)
                                firstItemFound = true;
                            //после первого успешного нахождения элемента меняем направление
                            if (searchBack && !goBack)
                                goBack = true;
                            IfpRecord ifp = IfpRecord.ReadLeader(Ifp, item.FullOffset);
                            //выводим только термины, где есть ссылки
                            if (ifp.TotalLinkCount > 0)
                            {
                                result.Add(new SearchTermInfo
                                {
                                    Text = item.Text,
                                    Count = ifp.TotalLinkCount,
                                    NodeNumber = goodItem.NodeNumber,
                                    LeafNodeNumber = item.NodeNumber,
                                    FullOffset = item.FullOffset
                                });
                                //если задано ограничение, выходим
                                if (limit > 0 && result.Count >= limit)
                                    goto DONE;
                            }
                        }
                    }
                    if (goBack && currentNode.Leader.Previous > 0)
                        currentNode = ReadPrevious(currentNode);
                    else if (currentNode.Leader.Next > 0)
                        currentNode = ReadNext(currentNode);
                    else
                        break;

                }

            }

        DONE:
            var terms = result.ToArray();
            result.Clear();
            return terms;
        }

        /// <summary>
        /// ibatrak поиск термина с точным совпаденем без чтения ссылок
        /// </summary>
        public SearchTermInfo SearchTermExact(string key)
        {
            return SearchClosestLeaf(key, true);
        }

        /// <summary>
        /// ibatrak поиск термина с точным совпаденем без чтения ссылок
        /// </summary>
        public SearchTermInfo SearchClosestLeaf(string key, bool exactMatch)
        {
            if (string.IsNullOrEmpty(key)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
                return null;

            key = key.ToUpperInvariant();

            //ibatrak ирбис читает номер, потом отдельно блоки
            //NodeRecord firstNode = ReadNode(1);
            //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord rootNode = ReadNode(firstNodeNumber);
            NodeRecord currentNode = rootNode;

            NodeItem goodItem = null;
            while (true)
            {
                //ibatrak если база пустая, на выход
                //if (currentNode.Items.Count == 0)
                //    return null;
                bool found = false;
                bool beyond = false;
                //goodItem = null;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, key);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;

                    //ibatrak перенесено в цикл FOUND
                    //if ((compareResult == 0)
                    //    && currentNode.IsLeaf)
                    //{
                    //    goto FOUND;
                    //}
                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        //ibatrak делаем цикл по leaf ноду отдельно, 
                        //как в других методах, чтобы иметь доступ и к номеру узла и к номеру листа
                        ////ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
                        //if (currentNode.IsLeaf)
                        //    return null;

                        //currentNode = goodItem.RefersToLeaf
                        //    ? ReadLeaf(goodItem.LowOffset)
                        //    : ReadNode(goodItem.LowOffset);
                        if (goodItem.RefersToLeaf)
                        {
                            goto FOUND;
                        }
                        //для отладки нарушения структуры инвертного файла, можно занулить goodItem перед циклом
                        //если оставить как есть будет зацикливание
                        if (currentNode.Leader.Number == goodItem.LowOffset)
                            throw new InvalidOperationException(String.Format("Адрес следующего блока совпадает: node={0}, item.node={1}, item.text={2}", currentNode.Leader.Number, goodItem.NodeNumber, goodItem.Text));
                        currentNode = ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    //ibatrak делаем цикл по leaf ноду отдельно, 
                    //как в других методах, чтобы иметь доступ и к номеру узла и к номеру листа
                    ////ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
                    //if (currentNode.IsLeaf)
                    //    return null;

                    //currentNode = goodItem.RefersToLeaf
                    //    ? ReadLeaf(goodItem.LowOffset)
                    //    : ReadNode(goodItem.LowOffset);
                    if (goodItem.RefersToLeaf)
                    {
                        goto FOUND;
                    }
                    currentNode = ReadNode(goodItem.LowOffset);
                }
                //Console.WriteLine(currentNode);
            }

        FOUND:
            if (goodItem != null)
            {
                //ibatrak переделано на цикл по leaf ноду, чтобы иметь доступ и к номеру узла и 
                //к номеру листа
                //IfpRecord ifp = IfpRecord.ReadLeader(Ifp, goodItem.FullOffset);
                //return new SearchTermInfo
                //{
                //    Text = goodItem.Text,
                //    Count = ifp.TotalLinkCount,
                //    LeafNodeNumber = goodItem.NodeNumber,
                //    FullOffset = goodItem.FullOffset
                //};

                currentNode = ReadLeaf(goodItem.LowOffset);
                while (true)
                {
                    foreach (NodeItem item in currentNode.Items)
                    {
                        int compareResult = string.CompareOrdinal(item.Text, key);
                        //если мы уже получили ключ дальше стоящий по сортировке, то дальше смотреть смысла нет
                        if (exactMatch && compareResult > 0)
                            return null;
                        if (exactMatch ? compareResult == 0 : compareResult >= 0)
                        {
                            IfpRecord ifp = IfpRecord.ReadLeader(Ifp, item.FullOffset);
                            return new SearchTermInfo
                            {
                                Text = item.Text,
                                Count = ifp.TotalLinkCount,
                                NodeNumber = goodItem.NodeNumber,
                                LeafNodeNumber = item.NodeNumber,
                                FullOffset = item.FullOffset
                            };
                        }
                    }
                    if (currentNode.Leader.Next > 0)
                        currentNode = ReadNext(currentNode);
                    else
                        break;
                }

            }
            return null;
        }

        /// <summary>
        /// ibatrak поиск ближайшего кюча в n01
        /// </summary>
        public SearchTermInfo SearchClosestNode(string key, int lastLevel)
        {
            if (string.IsNullOrEmpty(key)
                /*ibatrak если база пустая, на выход*/
                || _n01.Length == 0)
                return null;

            key = key.ToUpperInvariant();

            //ibatrak ирбис читает номер, потом отдельно блоки
            //NodeRecord firstNode = ReadNode(1);
            //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
            int firstNodeNumber = ReadFirstNodeNumber();
            NodeRecord rootNode = ReadNode(firstNodeNumber);
            NodeRecord currentNode = rootNode;

            NodeItem goodItem = null;
            int level = firstNodeNumber;
            while (true)
            {
                //ibatrak если база пустая, на выход
                //if (currentNode.Items.Count == 0)
                //    return null;
                bool found = false;
                bool beyond = false;
                //goodItem = null;

                foreach (NodeItem item in currentNode.Items)
                {
                    int compareResult = string.CompareOrdinal(item.Text, key);
                    if (compareResult > 0)
                    {
                        beyond = true;
                        break;
                    }

                    goodItem = item;
                    found = true;

                    //ibatrak перенесено в цикл FOUND
                    //if ((compareResult == 0)
                    //    && currentNode.IsLeaf)
                    //{
                    //    goto FOUND;
                    //}
                }
                if (goodItem == null)
                {
                    break;
                }
                if (found)
                {
                    if (beyond || (currentNode.Leader.Next == -1))
                    {
                        //ibatrak делаем цикл по leaf ноду отдельно, 
                        //как в других методах, чтобы иметь доступ и к номеру узла и к номеру листа
                        ////ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
                        //if (currentNode.IsLeaf)
                        //    return null;

                        //currentNode = goodItem.RefersToLeaf
                        //    ? ReadLeaf(goodItem.LowOffset)
                        //    : ReadNode(goodItem.LowOffset);
                        if (goodItem.RefersToLeaf)
                        {
                            goto FOUND;
                        }
                        //для отладки нарушения структуры инвертного файла, можно занулить goodItem перед циклом
                        //если оставить как есть будет зацикливание
                        if (currentNode.Leader.Number == goodItem.LowOffset)
                            throw new InvalidOperationException(String.Format("Адрес следующего блока совпадает: node={0}, item.node={1}, item.text={2}", currentNode.Leader.Number, goodItem.NodeNumber, goodItem.Text));
                        if (lastLevel > 1)
                        {
                            if (level < lastLevel)
                                return null;
                            //если мы достигли требуемого уровня, выходим
                            if (level == lastLevel)
                                goto FOUND;
                            level = ReadFirstItemLowOffset(level);
                        }
                        currentNode = ReadNode(goodItem.LowOffset);
                    }
                    else
                    {
                        currentNode = ReadNext(currentNode);
                    }
                }
                else
                {
                    //ibatrak делаем цикл по leaf ноду отдельно, 
                    //как в других методах, чтобы иметь доступ и к номеру узла и к номеру листа
                    ////ibatrak если мы здесь, уже спустились до уровня l01, а ключа с точным совпадением нет, то дальше искать смысла нет
                    //if (currentNode.IsLeaf)
                    //    return null;

                    //currentNode = goodItem.RefersToLeaf
                    //    ? ReadLeaf(goodItem.LowOffset)
                    //    : ReadNode(goodItem.LowOffset);
                    if (goodItem.RefersToLeaf)
                    {
                        goto FOUND;
                    }
                    if (lastLevel > 1)
                    {
                        if (level < lastLevel)
                            return null;
                        //если мы достигли требуемого уровня, выходим
                        if (level == lastLevel)
                            goto FOUND;
                        level = ReadFirstItemLowOffset(level);
                    }
                    currentNode = ReadNode(goodItem.LowOffset);
                }
                //Console.WriteLine(currentNode);
            }

        FOUND:
            if (goodItem != null)
            {
                //нужна информация по n01
                return new SearchTermInfo
                {
                    Text = goodItem.Text,
                    NodeNumber = goodItem.NodeNumber,
                    LeafNodeNumber = Math.Abs(goodItem.LowOffset),
                    FullOffset = goodItem.FullOffset
                };

            }
            return null;
        }

        ///// <summary>
        ///// ibatrak поиск термина в n01 на самом нижнем уровне дерева, там где ссылки на l01
        ///// </summary>
        //public SearchTermInfo SearchNodeTerm(string key)
        //{
        //    if (string.IsNullOrEmpty(key))
        //        return null;
        //    //блок №1 - первый блок в цепочке блоков самого нижнего уровня, там где ссылки на l01
        //    //поэтому номер блока вершины дерева, хранится отдельно,
        //    //он равен 1 только в небольшой базе, где всего 1 блок в n01
        //    return SearchNodeTerm(key, 1);
        //}

        ///// <summary>
        ///// ibatrak поиск термина в n01 на одном уровне дерева
        ///// </summary>
        //public SearchTermInfo SearchNodeTerm(string key, int firstNodeNumber)
        //{
        //    if (string.IsNullOrEmpty(key)
        //        /*ibatrak если база пустая, на выход*/
        //        || _n01.Length == 0)
        //        return null;

        //    key = key.ToUpperInvariant();

        //    //ibatrak ирбис читает номер, потом отдельно блоки
        //    //NodeRecord firstNode = ReadNode(1);
        //    //NodeRecord rootNode = ReadNode(firstNode.Leader.Number);
        //    //int firstNodeNumber = ReadFirstNodeNumber();
        //    NodeRecord rootNode = ReadNode(firstNodeNumber);
        //    NodeRecord currentNode = rootNode;

        //    NodeItem goodItem = null;
        //    while (true)
        //    {
        //        //ibatrak если база пустая, на выход
        //        //if (currentNode.Items.Count == 0)
        //        //    return null;
        //        bool found = false;
        //        bool beyond = false;

        //        foreach (NodeItem item in currentNode.Items)
        //        {
        //            int compareResult = string.CompareOrdinal(item.Text, key);
        //            if (compareResult > 0)
        //            {
        //                beyond = true;
        //                break;
        //            }

        //            goodItem = item;
        //            found = true;
        //        }
        //        if (goodItem == null)
        //        {
        //            break;
        //        }
        //        if (found)
        //        {
        //            if (beyond || (currentNode.Leader.Next == -1))
        //            {
        //                //переходы на следующий уровень и на листья не нужны, поиск только в пределах текущего уровня 
        //                if (goodItem.RefersToLeaf)
        //                {
        //                    //блоки самого нижнего уровня могут ссылаться на листья, ключи оглавления - только на другие блоки n01
        //                    if (firstNodeNumber > 1)
        //                        throw new InvalidOperationException("Ключи в дереве оглавления не могут ссылаться листья");
        //                    goto FOUND;
        //                }
        //                goto FOUND;

        //                //переход от ключа блока верхнего уровня на следующий уровень
        //                //currentNode = ReadNode(goodItem.LowOffset);
        //            }
        //            else
        //            {
        //                currentNode = ReadNext(currentNode);
        //            }
        //        }
        //        else
        //        {
        //            //переходы на следующий уровень, поиск только в пределах текущего уровня 
        //            if (goodItem.RefersToLeaf)
        //            {
        //                //блоки самого нижнего уровня могут ссылаться на листья, ключи оглавления - только на другие блоки n01
        //                if (firstNodeNumber > 1)
        //                    throw new InvalidOperationException("Ключи в дереве оглавления не могут ссылаться листья");
        //                goto FOUND;
        //            }
        //            goto FOUND;
        //            //currentNode = ReadNode(goodItem.LowOffset);
        //        }
        //    }

        //FOUND:
        //    if (goodItem != null)
        //    {
        //        return new SearchTermInfo
        //        {
        //            Text = goodItem.Text,
        //            NodeNumber = goodItem.NodeNumber,
        //            LeafNodeNumber = Math.Abs(goodItem.LowOffset),
        //            FullOffset = goodItem.FullOffset
        //        };
        //    }

        //    return null;
        //}

        public int[] SearchSimple(string key)
        {
            if (string.IsNullOrEmpty(key))
            {
                return new int[0];
            }

            TermLink[] result = new TermLink[0];

            if (key.EndsWith("$"))
            {
                key = key.Substring(0, key.Length - 1);
                if (!string.IsNullOrEmpty(key))
                {
                    result = SearchStart(key);
                }
            }
            else
            {
                result = SearchExact(key);
            }

            return result
                .Select(link => link.Mfn)
                .Distinct()
                .ToArray();
        }

        #endregion

        #region IDisposable members

        public void Dispose()
        {
            if (_ifp != null)
            {
                try
                {
                    _ifp.Flush();
                    _ifp.Close();
                    _ifp.Dispose();
                }
                catch (ObjectDisposedException)
                {
                }
                _ifp = null;
            }
            if (_l01 != null)
            {
                try
                {
                    _l01.Flush();
                    _l01.Close();
                    _l01.Dispose();
                }
                catch (ObjectDisposedException)
                {
                }
                _l01 = null;
            }
            if (_n01 != null)
            {
                try
                {
                    _n01.Flush();
                    _n01.Close();
                    _n01.Dispose();
                }
                catch (ObjectDisposedException)
                {
                }
                _n01 = null;
            }
        }

        #endregion
    }
}
