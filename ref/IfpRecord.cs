/* IfpRecord.cs
 */

#region Using directives

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;


#endregion

namespace ManagedClient
{
    [Serializable]
    public sealed class IfpRecord
    {
        #region Nested types

        /// <summary>
        /// ibatrak структура с описанием спец блока
        /// </summary>
        private class SpecialPostingBlockEntry
        {
            public const int RecordSize = 24;

            /// <summary>
            /// 1-я ссылка из записи обыкновенного формата
            /// </summary>
            public TermLink FirstPosting { get; set; }
            /// <summary>
            /// адрес записи спец блока в файле
            /// </summary>
            public long FileOffset { get; set; }

            /// <summary>
            /// адрес записи обыкновенного формата в файле
            /// </summary>
            public long Offset { get; set; }

            public override string ToString()
            {
                return String.Format("ofs:{0}, posting: {1}", Offset, FirstPosting);
            }

            //public static SpecialPostingBlockEntry Read(Stream stream)
            //{
            //    var result = new SpecialPostingBlockEntry
            //    {
            //        FileOffset = stream.Position,
            //        FirstPosting = TermLink.Read(stream),
            //        Offset = stream.ReadInt64Network()
            //    };
            //    return result;
            //}

            public static SpecialPostingBlockEntry Read(byte[] buffer, int offset)
            {
                //ibatrak чтение из буфера
                var result = new SpecialPostingBlockEntry
                {
                    FirstPosting = TermLink.Read(buffer, offset),
                    Offset = buffer.ReadInt64Network(offset + TermLink.RecordSize)
                };
                return result;
            }

            //public static void Write(Stream stream, SpecialPostingBlockEntry entry)
            //{
            //    TermLink.Write(stream, entry.FirstPosting ?? new TermLink());
            //    stream.WriteInt64Network(entry.Offset);
            //}

            public static int Write(byte[] buffer, SpecialPostingBlockEntry entry, int offset)
            {
                var size = TermLink.Write(buffer, entry.FirstPosting, offset);
                offset += size;
                buffer.WriteInt64Network(entry.Offset, offset);
                size += 8;
                return size;
            }
        }
        #endregion

        #region Constants

        /// <summary>
        /// Число ссылок на термин, после превышения которого
        /// используется специальный блок ссылок.
        /// </summary>
        public const int MinPostingsInBlock = 256;

        /// <summary>
        /// ibatrak Число ссылок, которое помещается в блок
        /// </summary>
        public const int PostingsInBlock = 254;

        /// <summary>
        /// ibatrak размер лидера записи
        /// </summary>
        public const int LeaderSize = 20;

        /// <summary>
        /// ibatrak размер блока
        /// </summary>
        public const int BlockSize = 1000000;

        #endregion

        #region Properties

        //ibatrak отслеживание изменений
        private int _lowOffset;
        public int LowOffset
        {
            get { return _lowOffset; }
            set
            {
                if (_lowOffset != value)
                {
                    _changed = true;
                    _lowOffset = value;
                }
            }
        }
        //public int LowOffset { get; set; }

        //ibatrak отслеживание изменений
        private int _highOffset;
        public int HighOffset
        {
            get { return _highOffset; }
            set
            {
                if (_highOffset != value)
                {
                    _changed = true;
                    _highOffset = value;
                }
            }
        }
        //public int HighOffset { get; set; }

        /// <summary>
        /// ibatrak ссылка на следующую запись
        /// </summary>
        public long FullOffset
        {
            get { return unchecked((((long)HighOffset) << 32) + LowOffset); }
            set
            {
                //ibatrak сеттер добавил
                LowOffset = (int)(value & 0xFFFFFFFF);
                HighOffset = (int)(value >> 32);
            }
        }

        /// <summary>
        /// ibatrak признак последней записи в списке
        /// </summary>
        private bool Last
        {
            get { return LowOffset == -1 && HighOffset == -1; }
            set
            {
                if (value)
                {
                    LowOffset = -1;
                    HighOffset = -1;
                }
                else
                {
                    //не предусмотрено
                }
            }
        }

        /// <summary>
        /// ibatrak признак записи со спец блоком
        /// </summary>
        private bool Special
        {
            get { return LowOffset == -1001 && HighOffset == -1001; }
            set
            {
                if (value)
                {
                    LowOffset = -1001;
                    HighOffset = -1001;
                }
                else
                {
                    //не предусмотрено
                }
            }
        }

        //ibatrak отслеживание изменений
        private int _totalLinkCount;
        public int TotalLinkCount
        {
            get { return _totalLinkCount; }
            set
            {
                if (_totalLinkCount != value)
                {
                    _changed = true;
                    _totalLinkCount = value;
                }
            }
        }
        //public int TotalLinkCount { get; set; }

        //ibatrak отслеживание изменений
        private int _blockLinkCount;
        public int BlockLinkCount
        {
            get { return _blockLinkCount; }
            set
            {
                if (_blockLinkCount != value)
                {
                    _changed = true;
                    _blockLinkCount = value;
                }
            }
        }

        //public int BlockLinkCount { get; set; }

        //ibatrak отслеживание изменений
        private int _capacity;
        public int Capacity
        {
            get { return _capacity; }
            set
            {
                if (_capacity != value)
                {
                    _changed = true;
                    _capacity = value;
                }
            }
        }

        //public int Capacity { get; set; }

        public List<TermLink> Links { get { return _links; } }

        #endregion

        #region Construction

        #endregion

        #region Private members

        /// <summary>
        /// ibatrak адрес записи в файле
        /// </summary>
        private long _FileOffset;

        /// <summary>
        /// ibatrak отслеживание изменений
        /// </summary>
        private bool _changed = false;

        /// <summary>
        /// ibatrak Лидеры вложенных записей для обновления
        /// </summary>
        private IfpRecord[] _NestedRecordLeaders;

        /// <summary>
        /// ibatrak Спец блок
        /// </summary>
        private SpecialPostingBlockEntry[] _SpecialBlock;

        private readonly List<TermLink> _links = new List<TermLink>();

        #endregion

        #region Public methods

        /// <summary>
        /// ibatrak чтение заголовка записи IFP (для подсчета количества ссылок)
        /// </summary>
        public static IfpRecord ReadLeader
            (
                Stream stream,
                long offset
            )
        {
            //new ObjectDumper()
            //    .DumpStream(stream, offset, 100);

            stream.Position = offset;
            //ibatrak чтение за раз
            var buffer = new byte[LeaderSize];
            if (stream.Read(buffer, 0, buffer.Length) != buffer.Length)
                throw new IOException();

            IfpRecord result = new IfpRecord
            {
                LowOffset = buffer.ReadInt32Network(0),
                HighOffset = buffer.ReadInt32Network(4),
                TotalLinkCount = buffer.ReadInt32Network(8),
                BlockLinkCount = buffer.ReadInt32Network(12),
                Capacity = buffer.ReadInt32Network(16),
                _FileOffset = offset
            };
            return result;

            //IfpRecord result = new IfpRecord
            //    {
            //        LowOffset = stream.ReadInt32Network(),
            //        HighOffset = stream.ReadInt32Network(),
            //        TotalLinkCount = stream.ReadInt32Network(),
            //        BlockLinkCount = stream.ReadInt32Network(),
            //        Capacity = stream.ReadInt32Network(),
            //        _FileOffset = offset
            //    };
            //return result;
        }

        public static IfpRecord Read
            (
                Stream stream,
                long offset
            )
        {
            //new ObjectDumper()
            //    .DumpStream(stream, offset, 100);

            //ibatrak чтение лидера вынесено отдельно
            //stream.Position = offset;

            //IfpRecord result = new IfpRecord
            //    {
            //        LowOffset = stream.ReadInt32Network(),
            //        HighOffset = stream.ReadInt32Network(),
            //        TotalLinkCount = stream.ReadInt32Network(),
            //        BlockLinkCount = stream.ReadInt32Network(),
            //        Capacity = stream.ReadInt32Network(),
            //        _FileOffset = offset
            //    };

            IfpRecord result = ReadLeader(stream, offset);

            //ibatrak чтение вложенных записей в спец блоке
            //Специальный формат записи .ifp
            //В этом случае первой записью является специальный блок,
            //который представляет собой заголовок (обыкновенного формата), в котором смещения имеют специальные значения = -1001, и набор вхождений следующего формата:
            //Число бит	Параметр	Описание
            //32	POSTING	1-я ссылка из записи обыкновенного формата
            //32	LOW	младшее слово смещения на следующую запись (если нет 0)
            //32	HIGH	старшее слово смещения на следующую запись (если нет 0)
            //Число вхождений кратно 4. Записи, на которые ссылается специальный блок связаны между собой как описано выше.
            //Общее количество ссылок для данного термина сохраняется только в специальном блоке.
            if (result.Special)
            {
                //irbis64.dll делает так

                //читает первые 24 байта блока спец ссылок
                //берет первую запись, адрес из нее в файле и читает записей IFP
                //по количеству result.BlockLinkCount

                //записи спец блока идут по количеству Capacity
                //каждая указывает на запись обычного формата
                //также в каждой записи обычного формата FullOffset указывает на следующую запись (кроме последней)
                //это должно соответствовать

                var specBlock = new SpecialPostingBlockEntry[result.Capacity];
                var specBlockBuffer = new byte[result.Capacity * SpecialPostingBlockEntry.RecordSize];
                var fileOffset = stream.Position;
                if (stream.Read(specBlockBuffer, 0, specBlockBuffer.Length) != specBlockBuffer.Length)
                    throw new IOException();

                for (int i = 0; i < result.Capacity; i++)
                {
                    var entry = SpecialPostingBlockEntry.Read(specBlockBuffer, i * SpecialPostingBlockEntry.RecordSize);
                    entry.FileOffset = fileOffset + i + SpecialPostingBlockEntry.RecordSize;
                    specBlock[i] = entry;
                }

                //запомнить для редактирования
                result._SpecialBlock = specBlock;

                var nonEmptyEntries = specBlock.Where(e => e.Offset > 0).Count();
                if (nonEmptyEntries != result.BlockLinkCount)
                    throw new InvalidOperationException("Ошибка чтения ifp offset=" + offset);

                var nestedRecords = new IfpRecord[result.BlockLinkCount];
                for (int i = 0; i < result.BlockLinkCount; i++)
                {
                    if (specBlock[i].Offset <= 0 ||
                        (i > 0 && nestedRecords[i - 1].FullOffset != specBlock[i].Offset))
                        throw new InvalidOperationException("Ошибка чтения ifp offset=" + offset);
                    var nestedRecord = Read(stream, specBlock[i].Offset);
                    nestedRecords[i] = nestedRecord;
                }
                var links = nestedRecords.SelectMany(r => r.Links).ToArray();
                if (links.Length != result.TotalLinkCount)
                    throw new InvalidOperationException("Ошибка чтения ifp offset=" + offset);
                result.Links.AddRange(links);
                result._NestedRecordLeaders = nestedRecords.ToArray();
                foreach (var r in nestedRecords)
                {
                    r._links.Clear();
                }
                return result;
            }
            //ibatrak до сюда

            //ibatrak читаем ссылки за раз, так быстрее
            var linkBuffer = new byte[result.BlockLinkCount * TermLink.RecordSize];
            if (stream.Read(linkBuffer, 0, linkBuffer.Length) != linkBuffer.Length)
                throw new IOException();

            for (int i = 0; i < result.BlockLinkCount; i++)
            {
                TermLink link = TermLink.Read(linkBuffer, i * TermLink.RecordSize);
                result.Links.Add(link);
            }

            //for (int i = 0; i < result.BlockLinkCount; i++)
            //{
            //    TermLink link = TermLink.Read(stream);
            //    result.Links.Add(link);
            //}

            return result;
        }

        /// <summary>
        /// ibatrak Запись лидера записи ifp
        /// </summary>
        private static void WriteLeader(Stream stream, IfpRecord ifpRecord, long offset)
        {
            stream.Position = offset;
            //ibatrak запись за раз
            var buffer = new byte[LeaderSize];
            WriteLeader(buffer, ifpRecord, 0);
            stream.Write(buffer, 0, buffer.Length);
            stream.Flush();

            //stream.WriteInt32Network(ifpRecord.LowOffset);
            //stream.WriteInt32Network(ifpRecord.HighOffset);
            //stream.WriteInt32Network(ifpRecord.TotalLinkCount);
            //stream.WriteInt32Network(ifpRecord.BlockLinkCount);
            //stream.WriteInt32Network(ifpRecord.Capacity);
            //stream.Flush();
        }

        /// <summary>
        /// ibatrak Запись лидера записи ifp
        /// </summary>
        private static int WriteLeader(byte[] buffer, IfpRecord ifpRecord, int offset)
        {
            buffer.WriteInt32Network(ifpRecord.LowOffset, offset);
            buffer.WriteInt32Network(ifpRecord.HighOffset, offset + 4);
            buffer.WriteInt32Network(ifpRecord.TotalLinkCount, offset + 8);
            buffer.WriteInt32Network(ifpRecord.BlockLinkCount, offset + 12);
            buffer.WriteInt32Network(ifpRecord.Capacity, offset + 16);
            return LeaderSize;
        }

        /// <summary>
        /// ibatrak Запись данных обыкновенного формата
        /// </summary>        
        private static int Write(byte[] buffer, IfpRecord ifpRecord, int offset)
        {
            var size = WriteLeader(buffer, ifpRecord, offset);
            offset += size;

            for (int i = 0; i < ifpRecord.Links.Count; i++)
            {
                var linkSize = TermLink.Write(buffer, ifpRecord.Links[i], offset);
                offset += linkSize;
                size += linkSize;
            }
            return size;
        }

        /// <summary>
        /// ibatrak очистка полей с количеством ссылок в заголовке записи
        /// </summary>
        public static void ClearItems(Stream stream, long offset)
        {
            //в заголовке проставляем 0 записей, сами ссылки не трогаем
            //ирбис так делает, проверено
            var ifpRecord = ReadLeader(stream, offset);
            //в записи со спец блоком зануляется только TotalLinkCount и оба поля во вложенных записях 
            var special = ifpRecord.Special;
            if (!special)
                ifpRecord.BlockLinkCount = 0;
            ifpRecord.TotalLinkCount = 0;
            WriteLeader(stream, ifpRecord, offset);
            if (special)
            {
                //начитаем первую запись из спец блока, в ней ссылка на первую запись обыкновенного формата
                //остальные записи спец блока здесь не нужны

                var specBlock = new SpecialPostingBlockEntry[ifpRecord.Capacity];
                var specBlockBuffer = new byte[ifpRecord.Capacity * SpecialPostingBlockEntry.RecordSize];
                var fileOffset = stream.Position;
                if (stream.Read(specBlockBuffer, 0, specBlockBuffer.Length) != specBlockBuffer.Length)
                    throw new IOException();

                for (int i = 0; i < ifpRecord.Capacity; i++)
                {
                    var entry = SpecialPostingBlockEntry.Read(specBlockBuffer, i * SpecialPostingBlockEntry.RecordSize);
                    entry.FileOffset = fileOffset + i + SpecialPostingBlockEntry.RecordSize;
                    specBlock[i] = entry;
                }

                var nonEmptyEntries = specBlock.Where(e => e.Offset > 0).Count();
                if (nonEmptyEntries != ifpRecord.BlockLinkCount)
                    throw new InvalidOperationException("Ошибка чтения ifp offset=" + offset);

                var nestedRecords = new IfpRecord[ifpRecord.BlockLinkCount];

                for (int i = 0; i < ifpRecord.BlockLinkCount; i++)
                {
                    if (specBlock[i].Offset <= 0 ||
                        (i > 0 && nestedRecords[i - 1].FullOffset != specBlock[i].Offset))
                        throw new InvalidOperationException("Ошибка чтения ifp offset=" + offset);
                    var nestedRecord = ReadLeader(stream, specBlock[i].Offset);
                    nestedRecord.BlockLinkCount = 0;
                    nestedRecord.TotalLinkCount = 0;
                    nestedRecords[i] = nestedRecord;
                    WriteLeader(stream, ifpRecord, specBlock[i].Offset);
                }
            }
        }

        /// <summary>
        /// ibatrak установка ссылки на следующую запись
        /// </summary>
        private static void SetNext(IfpRecord ifpRecord, long next, TermLink[] links, int newBlocks)
        {
            if (ifpRecord.FullOffset == next || next == 0)
                throw new ArgumentException("Ошибка записи ifp: недопустимое значение адреса следующей записи", "next");
            //контроль правильности использования
            if (ifpRecord.FullOffset > 0)
                throw new InvalidOperationException("Ошибка записи ifp: перезаписывается не последняя запись в цепочке");
            if (!ifpRecord.Special)
                ifpRecord.FullOffset = next;
            else
            {
                if (ifpRecord._NestedRecordLeaders.Length + newBlocks > ifpRecord._SpecialBlock.Length)
                    throw new InvalidOperationException("Ошибка записи ifp: обновление спец блока превышает вместимость");

                //в последней имеющейся вложенной записи отметить адрес следующей записи 
                ifpRecord._NestedRecordLeaders[ifpRecord._NestedRecordLeaders.Length - 1].FullOffset = next;
                //требуется обновить заголовки записей и элементы спец блока по количеству вновь создаваемых блоков 
                //- то есть записей обычного формата
                for (int i = 0; i < newBlocks; i++)
                {
                    var specialBlockEntry = ifpRecord._SpecialBlock[ifpRecord._NestedRecordLeaders.Length + i];
                    if (specialBlockEntry.Offset != 0)
                        throw new InvalidOperationException("Ошибка записи ifp: обновление непустого элемента спец блока");

                    specialBlockEntry.Offset = next;
                    specialBlockEntry.FirstPosting = links[i * PostingsInBlock];

                    int linksCount = links.Skip(i * PostingsInBlock).Take(PostingsInBlock).Count();
                    next += /*размер новой записи обыкновенного формата*/ LeaderSize + linksCount * TermLink.RecordSize;
                }

                //обновим счетчик блоков
                ifpRecord.BlockLinkCount += newBlocks;
            }
        }

        ///// <summary>
        ///// ibatrak установка ссылки на следующую запись
        ///// </summary>
        //private static void SetNext(Stream stream, IfpRecord ifpRecord, long next, TermLink link, int newBlocks)
        //{
        //    if (ifpRecord.FullOffset != next && next > 0)
        //    {
        //        var r = ifpRecord;
        //        //поиск последней записи по цепочке
        //        //метод вызывается только для последней записи, потребности в этом нет
        //        //оставлено для совместимости                
        //        while (r.FullOffset > 0)
        //        {
        //            r = ReadLeader(stream, r.FullOffset);
        //        }
        //        if (r.Special)
        //        {
        //            //дальше работаем со вложенной записью
        //            var nestedRecord = r._NestedRecordLeaders[r._NestedRecordLeaders.Length - 1];

        //            //установка ссылки на новую запись в спец блок, если есть место
        //            if (r._NestedRecordLeaders.Length < r._SpecialBlock.Length)
        //            {
        //                var specialBlockEntry = r._SpecialBlock[r._NestedRecordLeaders.Length];
        //                if (specialBlockEntry.Offset == 0)
        //                {
        //                    specialBlockEntry.Offset = next;
        //                    specialBlockEntry.FirstPosting = link;
        //                    //обновим счетчик блоков
        //                    r.BlockLinkCount += newBlocks;

        //                    if (ifpRecord._NestedRecordLeaders == null || !ifpRecord._NestedRecordLeaders.Contains(nestedRecord))
        //                    {
        //                        //если запись не является вложенной, то записать спец блок
        //                        stream.Position = specialBlockEntry.FileOffset;
        //                        SpecialPostingBlockEntry.Write(stream, specialBlockEntry);
        //                    }
        //                }
        //            }
        //            r = nestedRecord;

        //        }
        //        r.FullOffset = next;
        //        //обновить ссылку на следующую запись в последней по цепочке записи, если она отличается от текущей
        //        //и не содержится во вложенных
        //        if (r != ifpRecord && (ifpRecord._NestedRecordLeaders == null || !ifpRecord._NestedRecordLeaders.Contains(r)))
        //            WriteLeader(stream, r, r._FileOffset);
        //    }

        //}

        /// <summary>
        /// Запись данных в простом формате или со спец блоками
        /// </summary>
        private static int Write(Stream stream, IfpRecord ifpRecord, long offset, bool padding)
        {
            int size = 0;
            byte[] buffer = null;
            //обработка обычной записи
            if (!ifpRecord.Special)
            {
                //в записи обыкновенного формата указываем либо указатель на следующую из параметров 
                //либо обозначаем последнюю запись
                size = LeaderSize + ifpRecord.Links.Count * TermLink.RecordSize;
                buffer = new byte[size];
                Write(buffer, ifpRecord, 0);
            }
            else
            {
                //обработка записи со спец блоком
                var links = ifpRecord.Links.ToArray();
                //если нет - делаем запись со спец-блоком
                //здесь записи делятся по 254, то есть будет минимум 2 блока
                var blockCount = ifpRecord._NestedRecordLeaders != null ? ifpRecord._NestedRecordLeaders.Length :
                    (int)Math.Ceiling((double)links.Length / (double)PostingsInBlock);

                int specialBlockSize = ifpRecord.Capacity * SpecialPostingBlockEntry.RecordSize;

                size = /*размер первой записи*/LeaderSize /*в первой записи ссылок нет*/ +
                    /*размер спец блока*/specialBlockSize +
                    (ifpRecord._NestedRecordLeaders == null ? /*размер вложенных записей только если они будут созданы*/
                    /*размер записей по числу блоков*/LeaderSize * blockCount + links.Length * TermLink.RecordSize : 0);

                buffer = new byte[size];

                ifpRecord.Links.Clear();
                //устанавливается через Special
                //ifpRecord.LowOffset = -1001;
                //ifpRecord.HighOffset = -1001;

                //уже сделали ifpRecord.Links.Clear(); будет запись только заголовка
                //int bufferOffset = Write(buffer, ifpRecord, 0);
                int bufferOffset = WriteLeader(buffer, ifpRecord, 0);


                //запись спец блока
                //пишем записи спец блока по количеству Capacity
                int linksWritten = 0;
                for (int i = 0; i < ifpRecord.Capacity; i++)
                {
                    int count = 0;

                    var entry = ifpRecord._SpecialBlock != null ? ifpRecord._SpecialBlock[i] : new SpecialPostingBlockEntry();
                    //генерация адресов для новых записей спец блока
                    if (ifpRecord._NestedRecordLeaders == null && i < blockCount)
                    {
                        //в ирбисе здесь номер слова из первой ссылки, зачем непонятно
                        entry.FirstPosting = links[linksWritten];
                        //ссылка на место за спец блоком + размер записей обыкновенного формата столько, 
                        //сколько указывают предыдущие записи спец блока
                        entry.Offset = offset +
                            /*размер первой записи*/ LeaderSize +
                            /*рамер спец блока*/ specialBlockSize +
                            /*размер записей обыкновенного формата*/ LeaderSize * i + linksWritten * TermLink.RecordSize;

                        //ifpRecord._NestedRecordLeaders уже null
                        //if (ifpRecord._NestedRecordLeaders != null)
                        //    count = Math.Min(links.Length - linksWritten, ifpRecord._NestedRecordLeaders[i].TotalLinkCount);
                        //else
                        //    count = Math.Min(links.Length - linksWritten, PostingsInBlock);

                        count = Math.Min(links.Length - linksWritten, PostingsInBlock);
                        linksWritten += count;
                    }
                    bufferOffset += SpecialPostingBlockEntry.Write(buffer, entry, bufferOffset);
                }

                linksWritten = 0;
                for (int i = 0; i < blockCount; i++)
                {
                    //если обновляется существующая запись, количество ссылок брать из существующих блоков
                    int count = 0;

                    IfpRecord nestedRecord = null;

                    //здесь пишем записи обычного формата
                    if (ifpRecord._NestedRecordLeaders != null)
                    {
                        //для старой вложенной записи перезаписываем блок по количеству записей в заголовке
                        //вместимость в ссылках и ссылки на следующие блоки не переписываем
                        count = Math.Min(links.Length - linksWritten, ifpRecord._NestedRecordLeaders[i].Capacity);
                        nestedRecord = ifpRecord._NestedRecordLeaders[i];
                        nestedRecord.TotalLinkCount = count;
                        nestedRecord.BlockLinkCount = count;
                    }
                    else
                    {
                        //для новой записи записываем PostingsInBlock
                        count = Math.Min(links.Length - linksWritten, PostingsInBlock);
                        nestedRecord = new IfpRecord
                        {
                            TotalLinkCount = count,
                            BlockLinkCount = count,
                            Capacity = count
                        };

                        if (i < blockCount - 1)
                        {
                            //ссылка на место сразу за этой записью
                            nestedRecord.FullOffset = offset +
                                /*размер первой записи*/ LeaderSize +
                                /*рамер спец блока*/ specialBlockSize +
                                /*размер предыдущих записей + размер этой записи*/LeaderSize * (i + 1) + (linksWritten + count) * TermLink.RecordSize;
                        }
                        else
                        {
                            //в последней записи обыкновенного формата обозначаем последнюю запись
                            nestedRecord.Last = true;
                        }
                    }

                    var linksBlock = new TermLink[count];
                    Array.Copy(links, linksWritten, linksBlock, 0, linksBlock.Length);
                    nestedRecord.Links.AddRange(linksBlock);
                    linksWritten += count;
                    //старые вложенные записи пишутся на старое место
                    if (ifpRecord._NestedRecordLeaders != null)
                        Write(stream, nestedRecord, nestedRecord._FileOffset, padding);
                    else
                        bufferOffset += Write(buffer, nestedRecord, bufferOffset);
                }
            }

            if (buffer.Length != size)
                throw new InvalidOperationException("Ошибка записи ifp");

            //выравнивание размера файла
            if (padding && (offset + buffer.Length) > stream.Length)
            {
                long newSize = LeaderSize + (long)Math.Ceiling((double)(offset + buffer.Length - LeaderSize) / (double)BlockSize) * BlockSize;
                stream.SetLength(newSize);
            }

            if (stream.Seek(offset, SeekOrigin.Begin) != offset)
            {
                throw new IOException();
            }

            stream.Write(buffer, 0, buffer.Length);
            stream.Flush();

            return size;
        }

        /// <summary>
        /// ibatrak замена ссылок с отслеживанием изменений
        /// </summary>
        private static void ReplaceLinks(IfpRecord ifpRecord, TermLink[] links, int length)
        {
            //если в записи больше элементов, то просто заменить содержимое
            if (ifpRecord.Links.Count > length)
            {
                ifpRecord._changed = true;
                ifpRecord.Links.Clear();
                for (int i = 0; i < length; i++)
                {
                    ifpRecord.Links.Add(links[i]);
                }
            }
            else
            {
                //замена элементов                
                int replaceCount = Math.Min(length, ifpRecord.Links.Count);
                for (int i = 0; i < replaceCount; i++)
                {
                    if (!ifpRecord.Links[i].Equals(links[i]))
                    {
                        ifpRecord.Links[i] = links[i];
                        ifpRecord._changed = true;
                    }
                }
                //добавление элементов
                if (length > replaceCount)
                {
                    ifpRecord._changed = true;
                    for (int i = replaceCount; i < length; i++)
                    {
                        ifpRecord.Links.Add(links[i]);
                    }
                }
            }
        }

        /// <summary>
        /// ibatrak добавление новой или обновление существующей записи
        /// </summary>
        public static int Write(Stream stream, NodeItem item, TermLink[] links, long offset, bool padding)
        {
            int size = 0;
            IfpRecord ifpRecord = null;
            //повторное использование существующих записей
            long oldOffset = item.FullOffset;
            //если элемент новый - отметить в нем ссылку на запись ifp
            if (item.FullOffset == 0)
                item.FullOffset = offset;
            int capacity = 0;
            //требуется писать записи обыкновенного формата, в случае расширения старой записи
            bool expanding = false;

            if (oldOffset > 0)
            {
                bool topRecord = true;
                int linksCount = links.Length;
                //перезаписываем в цикле все записи по цепочке
                while (true)
                {
                    //начитаем старую версию записи с нужным объемом или последнюю в цепочке
                    ifpRecord = Read(stream, oldOffset);

                    //в записи со спец блоком реальная вместимость записи в ссылках считается по вложенным записям
                    capacity = ifpRecord.Special ? ifpRecord._NestedRecordLeaders.Sum(r => r.Capacity) : ifpRecord.Capacity;

                    bool last = ifpRecord.Last;
                    //если в старой записи хватает места, перезапишем ее
                    if (links.Length <= capacity)
                    {
                        ifpRecord._changed = false;
                        ReplaceLinks(ifpRecord, links, links.Length);

                        //счетчик ссылок обновим
                        ifpRecord.TotalLinkCount = links.Length;
                        if (!ifpRecord.Special)
                            ifpRecord.BlockLinkCount = links.Length;
                        //запись в файл только при наличии изменений
                        if (ifpRecord._changed)
                            Write(stream, ifpRecord, oldOffset, false /*при обновлении записей всегда padding = false*/);
                        links = null;
                    }
                    else //перезапись старой записи при расширении
                    {
                        expanding = true;

                        //ирбис до упора не заполняет, при расширении делит пополам
                        //уменьшение размеров последнего блока возможно, если 
                        //количество новых элементов плюс половина последнего блока не превышают размер блока
                        int countToAdd = 0;
                        //запись со спец блоком в цепочке быть не может
                        //деление записей происходит только в последней по цепочке записи
                        int newLinksCount = links.Length - capacity;
                        if (!ifpRecord.Special)
                        {
                            //половина последнего блока + количество новых ссылок вмещается в блок, тогда делим
                            if (last && capacity > 1 &&
                                ((int)Math.Ceiling((double)capacity / 2d) + newLinksCount) <= PostingsInBlock)
                                countToAdd = (int)Math.Ceiling((double)capacity / 2d);
                            else
                                countToAdd = capacity;
                        }
                        else
                        {
                            //запись со спец блоком
                            //половина последнего блока + количество новых ссылок вмещается в блок, тогда делим
                            if (((int)Math.Ceiling((double)ifpRecord._NestedRecordLeaders[ifpRecord._NestedRecordLeaders.Length - 1].Capacity / 2d) + newLinksCount) <= PostingsInBlock)
                            {
                                //в записи со спец блоком последняя делится пополам
                                countToAdd = capacity - (int)Math.Ceiling((double)ifpRecord._NestedRecordLeaders[ifpRecord._NestedRecordLeaders.Length - 1].Capacity / 2d);
                            }
                            else
                                countToAdd = capacity;
                        }

                        //if (!last)
                        //    countToAdd = capacity;
                        //else
                        //{
                        //    if (!ifpRecord.Special)
                        //        countToAdd = capacity > 1 ? (int)Math.Ceiling((double)capacity / 2d) : capacity;
                        //    else //в записи со спец блоком прследняя делится пополам
                        //        countToAdd = capacity - (int)Math.Ceiling((double)ifpRecord._NestedRecordLeaders[ifpRecord._NestedRecordLeaders.Length - 1].Capacity / 2d);
                        //}
                        //если в старой записи не хватает места, перезапишем в нее сколько влезет
                        //остальное запишем в новую запись
                        ifpRecord._changed = false;
                        ReplaceLinks(ifpRecord, links, countToAdd);
                        //ifpRecord.Links.Clear();                        
                        //ifpRecord.Links.AddRange(links.Take(countToAdd).ToArray());
                        //счетчик ссылок обновим              
                        //верхняя в цепочке запись получает в заголовке полное количество ссылок
                        if (topRecord)
                            ifpRecord.TotalLinkCount = linksCount;
                        else
                            ifpRecord.TotalLinkCount = countToAdd;

                        //в обычной записи здесь ставится количество записей в блоке
                        if (!ifpRecord.Special)
                            ifpRecord.BlockLinkCount = countToAdd;
                        //так быстрее, чем ToArray
                        Array.Copy(links, countToAdd, links, 0, links.Length - countToAdd);
                        Array.Resize(ref links, links.Length - countToAdd);
                        //links = links.Skip(countToAdd).ToArray();                        

                        //установка ссылки на следующую запись если мы достигли конца цепочки для обычных записей
                        //для записи со спец блоком будет расширение спец блока и там установка ссылки на следующую запись
                        int newBlocks = (int)Math.Ceiling((double)links.Length / (double)PostingsInBlock);
                        //расширение записи со спец блоком идет не на одну запись, а по количеству блоков
                        //if (last || (ifpRecord.Special && ifpRecord._NestedRecordLeaders.Length < ifpRecord.Capacity))
                        if (last || (ifpRecord.Special && ifpRecord._NestedRecordLeaders.Length + newBlocks <= ifpRecord.Capacity))
                        {
                            SetNext(ifpRecord, offset, links, newBlocks);
                            //SetNext(stream, ifpRecord, offset, links[0], newBlocks);
                        }
                        //если расширяется запись со спец блоком, то лидер записи и новый спец блок помещаются в другое место
                        //в новом спец блоке добавляется 4 блока
                        //else if (ifpRecord.Special && ifpRecord._NestedRecordLeaders.Length >= ifpRecord.Capacity)
                        else if (ifpRecord.Special && ifpRecord._NestedRecordLeaders.Length + newBlocks > ifpRecord.Capacity)
                        {
                            var newLeader = new IfpRecord();
                            newLeader.Special = true;

                            var specialBlock = ifpRecord._SpecialBlock;
                            int count = specialBlock.Length;
                            int newCapacity = 4 * (int)Math.Ceiling(((double)ifpRecord._NestedRecordLeaders.Length + (double)newBlocks) / 4d);
                            Array.Resize(ref specialBlock, newCapacity);
                            for (int i = count; i < specialBlock.Length; i++)
                            {
                                specialBlock[i] = new SpecialPostingBlockEntry();
                            }

                            newLeader.Capacity = newCapacity;
                            newLeader.TotalLinkCount = linksCount;
                            //count - это количество элементов в спец блоке всего, надо количество непустых элементов
                            //newLeader.BlockLinkCount = count /*при вызове SetNext будет инкремент*/;
                            newLeader.BlockLinkCount = ifpRecord.BlockLinkCount /*при вызове SetNext будет инкремент*/;

                            int newLeaderSize = LeaderSize + newLeader.Capacity * SpecialPostingBlockEntry.RecordSize;
                            newLeader._SpecialBlock = specialBlock;

                            newLeader._NestedRecordLeaders = ifpRecord._NestedRecordLeaders;
                            //newLeader._NestedRecordLeaders используется для SetNext
                            SetNext(newLeader, offset + newLeaderSize, links, newBlocks);
                            //SetNext(stream, newLeader, offset + newLeaderSize, links[0], newBlocks);
                            newLeader._NestedRecordLeaders = null;

                            //в элементе надо заменить адрес старой записи
                            item.FullOffset = offset;

                            Write(stream, newLeader, offset, true);

                            offset += newLeaderSize;
                            size += newLeaderSize;
                        }

                        if (ifpRecord._changed)
                            Write(stream, ifpRecord, oldOffset, false /*при обновлении записей всегда padding = false*/);
                    }

                    if (last || ifpRecord.FullOffset <= 0 || links == null || links.Length == 0)
                    {
                        //если будем расширять запись со спец блоком, то максимальный размер у нее не более PostingsInBlock
                        if (ifpRecord.Special)
                            capacity = PostingsInBlock;
                        break;
                    }
                    oldOffset = ifpRecord.FullOffset;
                    topRecord = false;
                }
            }
            //добавление новой записи
            if (links != null && links.Length > 0)
            {
                //при расширении записи всегда пишем записи обычного формата
                //здесь назначаем емкость записи
                //if (ifpRecord.Links.Count < MinPostingsInBlock)
                if (expanding || links.Length < MinPostingsInBlock)
                {
                    //делаем несколько блоков только если идет расширение старой записи
                    int blockCount = expanding ? (int)Math.Ceiling((double)links.Length / (double)PostingsInBlock) : 1;
                    for (int i = 0; i < blockCount; i++)
                    {
                        var lastBlock = i == blockCount - 1;
                        ifpRecord = new IfpRecord();
                        ifpRecord.Links.AddRange(blockCount == 1 ? links : links.Skip(i * PostingsInBlock).Take(PostingsInBlock));
                        //при расширении записи следующая запись получает столько ссылок, сколько емкость предыдущей записи + 1
                        int count = ifpRecord.Links.Count;
                        int recCapacity = 0;
                        if (lastBlock && capacity > 0)
                        {
                            recCapacity = Math.Max(capacity, ifpRecord.Links.Count) + 1;
                            for (int j = count; j < recCapacity; j++)
                            {
                                ifpRecord.Links.Add(new TermLink());
                            }
                        }
                        else
                            recCapacity = count;
                        ifpRecord.TotalLinkCount = count;
                        ifpRecord.BlockLinkCount = count;
                        ifpRecord.Capacity = recCapacity;
                        ifpRecord.Last = lastBlock;
                        //у непоследней записи нужно установить ссылку на следующую
                        if (!lastBlock)
                            ifpRecord.FullOffset = offset + /*размер ifp записи обычного формата*/ LeaderSize + count * TermLink.RecordSize;
                        int written = Write(stream, ifpRecord, offset, padding);
                        offset += written;
                        size += written;
                    }
                }
                else
                {
                    //новая запись со спецблоками только в случае создания новой,
                    //при расширении всегда идут записи обыкновенного формата
                    ifpRecord = new IfpRecord();
                    ifpRecord.Links.AddRange(links);
                    //для новой записи здесь нужно обозначить спец блок
                    //при создании новой записи со спец блоком ирбис не выравнивает количество записей под размер блока
                    //если в последствии такую запись расширяют,
                    //то добавляется еще одна запись обычного формата и дальше по обычной схеме
                    ifpRecord.Special = true;
                    ifpRecord.TotalLinkCount = links.Length;
                    //в записи со спец блоком здесь количество вложенных записей
                    ifpRecord.BlockLinkCount = (int)Math.Ceiling((double)links.Length / (double)PostingsInBlock);
                    //в записи со спецблоками в поле емкость ставится количество вложенных записей кратное 4
                    //емкость выставляется кратно 4, реальное количество блоков в BlockLinkCount
                    ifpRecord.Capacity = 4 * (int)Math.Ceiling((double)links.Length / (double)PostingsInBlock / 4d);

                    size += Write(stream, ifpRecord, offset, padding);
                }

            }
            ////если элемент новый - отметить в нем ссылку на запись ifp
            //if (item.FullOffset == 0)
            //    item.FullOffset = offset;
            return size;
        }

        #endregion

        #region Object members

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            foreach (TermLink link in Links)
            {
                builder.AppendLine(link.ToString());
            }

            return string.Format
                (
                    "LowOffset: {0}, HighOffset: {1}, TotalLinkCount: {2}, "
                    + "BlockLinkCount: {3}, Capacity: {4}\r\nItems: {5}",
                    LowOffset,
                    HighOffset,
                    TotalLinkCount,
                    BlockLinkCount,
                    Capacity,
                    builder
                );
        }

        #endregion
    }
}
