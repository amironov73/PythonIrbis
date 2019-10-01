/* IrbisDirectReader.cs
 */

#region Using directives

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using ManagedClient;
using WebIrbisNet.Irbis64;
using log4net;

#endregion

namespace ManagedClient
{
    //ibatrak переименовал читалку в IO
    //public sealed class IrbisDirectReader
    public sealed class IrbisDirectIO
        : IIrbis64IO, IDisposable
    {
        #region Properties

        public MstFile Mst { get; private set; }

        public XrfFile Xrf { get; private set; }

        public InvertedFile InvertedFile { get; private set; }

        public string Database { get; private set; }

        #endregion

        #region Construction

        public IrbisDirectIO
            (
                string masterFile,
                bool write
            )
        {
            Database = Path.GetFileNameWithoutExtension(masterFile);
            Mst = new MstFile
                (
                    Path.ChangeExtension
                        (
                            masterFile,
                            ".mst"
                        ),
                        write
                );
            Xrf = new XrfFile
                (
                    Path.ChangeExtension
                    (
                        masterFile,
                        ".xrf"
                    ),
                    write
                );
            InvertedFile = new InvertedFile
                (
                    Path.ChangeExtension
                    (
                        masterFile,
                        ".ifp"
                    ),
                    write
                );
        }

        #endregion

        #region Private members

        #endregion

        #region Public methods

        public void OpenDb(string db)
        {
            OpenDb(db, false);
        }

        public void OpenDb(string db, bool write)
        {
            var masterFile = Irbis64Config.LookupDbMst(db);
            Database = db;
            Database = Path.GetFileNameWithoutExtension(masterFile);

            if (Mst != null)
                Mst.Dispose();
            if (Xrf != null)
                Xrf.Dispose();
            if (InvertedFile != null)
                InvertedFile.Dispose();

            Mst = new MstFile
                (
                    Path.ChangeExtension
                        (
                            masterFile,
                            ".mst"
                        ),
                        write
                );
            Xrf = new XrfFile
                (
                    Path.ChangeExtension
                    (
                        masterFile,
                        ".xrf"
                    ),
                    write
                );
            InvertedFile = new InvertedFile
                (
                    Path.ChangeExtension
                    (
                        masterFile,
                        ".ifp"
                    ),
                    write
                );
        }

        //ibatrak событие для обработки кодов ирбис
        private Irbis64CodeEventArgs _codeArgs = new Irbis64CodeEventArgs();

        public event Irbis64CodeEventHandler Irbis64Code;

        private void OnIrbis64Code(int code)
        {
            _codeArgs.Code = code;
            if (Irbis64Code != null)
                Irbis64Code(this, _codeArgs);
        }

        public int GetMaxMfn()
        {
            Mst.ReadControlRecord();
            return Mst.ControlRecord.NextMfn - 1;
        }

        public bool IsDbLocked()
        {
            return Mst.ReadDatabaseLockedFlag();
        }

        /// <summary>
        /// ibatrak чтение статуса записи
        /// </summary>
        public RecordStatus? ReadStatus(int mfn)
        {
            var xrfRecord = GetXrfRecordError(mfn, RecordStatus.PhysicallyDeleted | RecordStatus.Absent);
            if (_codeArgs.Code != 0)
                return null;
            return xrfRecord.Status;
        }

        /// <summary>
        /// ibatrak прочитать версию записи
        /// </summary>
        public int ReadVersion(int mfn)
        {
            var xrfRecord = GetXrfRecordError(mfn, RecordStatus.PhysicallyDeleted | RecordStatus.Absent);
            if (_codeArgs.Code != 0)
                return 0;
            var result = Mst.ReadVersion(xrfRecord.Offset);
            return result;
        }

        /// <summary>
        /// ibatrak чтение записи N шагов назад
        /// </summary>
        public IrbisRecord ReadRecord(int mfn, int stepsBack)
        {
            var version = ReadVersion(mfn);
            if (_codeArgs.Code != 0)
                return null;
            if (stepsBack <= 0 || version <= stepsBack)
            {
                OnIrbis64Code(-201 /*ERR_OLDREC_ABSENT*/);
                return null;
            }

            //здесь можно читать логически удаленные записи
            var xrfRecord = GetXrfRecordError(mfn, RecordStatus.PhysicallyDeleted | /*RecordStatus.LogicallyDeleted |*/ RecordStatus.Absent);
            if (_codeArgs.Code != 0)
                return null;

            IrbisRecord rec = null;
            var leader = Mst.ReadRecordLeader(xrfRecord.Offset);
            for (int i = 0; i < stepsBack; i++)
            {
                if (i < stepsBack - 1)
                    leader = Mst.ReadRecordLeader(leader.Previous);
                else
                {
                    var result = Mst.ReadRecord(leader.Previous);
                    result.Database = Database;
                    rec = result;
                }
            }
            rec.Database = Database;
            //в записи MST пишутся одни флаги, в XRF - другие
            //в результирующей записи нужно иметь комбинированный статус
            rec.Status |= xrfRecord.Status;
            return rec;
        }

        /// <summary>
        /// ibatrak чтение записи с проверкой
        /// </summary>
        public IrbisRecord ReadRecord(int mfn)
        {
            var xrfRecord = GetXrfRecordError(mfn, RecordStatus.PhysicallyDeleted | RecordStatus.LogicallyDeleted | RecordStatus.Absent);
            if (_codeArgs.Code != 0)
                return null;
            IrbisRecord result = Mst.ReadRecord(xrfRecord.Offset);
            result.Database = Database;
            //в записи MST пишутся одни флаги, в XRF - другие
            //в результирующей записи нужно иметь комбинированный статус
            result.Status |= xrfRecord.Status;
            return result;


            //XrfRecord xrfRecord = Xrf.ReadRecord(mfn);
            ////ibatrak если запись удалена физически, не читать
            //if (Convert.ToBoolean(xrfRecord.Status & RecordStatus.PhysicallyDeleted))
            //    return null;
            //MstRecord mstRecord = Mst.ReadRecord2(xrfRecord.Offset);
            //IrbisRecord result = mstRecord.DecodeRecord();
            //result.Database = Database;
            //return result;
        }

        /// <summary>
        /// ibatrak чтение записи с проверкой только на физическое удаление
        /// </summary>
        public IrbisRecord ReadExistingRecord(int mfn)
        {
            var xrfRecord = GetXrfRecordError(mfn, RecordStatus.PhysicallyDeleted | RecordStatus.Absent);
            if (_codeArgs.Code != 0)
                return null;
            IrbisRecord result = Mst.ReadRecord(xrfRecord.Offset);
            result.Database = Database;
            //в записи MST пишутся одни флаги, в XRF - другие
            //в результирующей записи нужно иметь комбинированный статус
            result.Status |= xrfRecord.Status;
            return result;
        }

        /// <summary>
        /// ibatrak добавление / обновление записи
        /// </summary>
        public void WriteRecord(IrbisRecord record, bool padding)
        {
            //Mst.LockDatabase(true);
            if (record.Mfn <= 0)
            {
                record.Version = 1;
                record.PreviousOffset = 0;
                var offset = Mst.AddRecord(record, padding);
                Xrf.WriteRecord(new XrfRecord { Mfn = record.Mfn, Offset = offset, Status = RecordStatus.NonActualized }, padding);
                OnIrbis64Code(0);
            }
            else
            {
                //XrfRecord xrfRecord = Xrf.ReadRecord(record.Mfn);
                XrfRecord xrfRecord = GetXrfRecordError(record.Mfn, RecordStatus.Locked | RecordStatus.LogicallyDeleted | RecordStatus.PhysicallyDeleted | RecordStatus.Absent);
                if (_codeArgs.Code == 0)
                {
                    long offset = xrfRecord.Offset;
                    int version = Mst.ReadVersion(xrfRecord.Offset);
                    record.Version = version + 1;
                    record.PreviousOffset = xrfRecord.Offset;
                    //предыдущую версию записи пометить как неактуализированную
                    Mst.UpdateRecordStatus(RecordStatus.NonActualized, offset);
                    offset = Mst.UpdateRecord(record, RecordStatus.Last | RecordStatus.NonActualized, padding);
                    xrfRecord.Offset = offset;
                    xrfRecord.Status = RecordStatus.NonActualized;
                    Xrf.WriteRecord(xrfRecord, padding);
                }
            }
            //Mst.LockDatabase(false);
        }

        /// <summary>
        /// ibatrak блокировка / разблокировка записи с проверкой
        /// </summary>
        public void LockRecord(int mfn, bool flag)
        {
            var status = RecordStatus.LogicallyDeleted | RecordStatus.PhysicallyDeleted | RecordStatus.Absent;
            //статус блокировки ошибкой считать только при попытке заблокировать
            if (flag)
                status |= RecordStatus.Locked;

            XrfRecord xrfRecord = GetXrfRecordError(mfn, status);
            if (_codeArgs.Code == 0 && flag != xrfRecord.Locked)
            {
                //ibatrak установка флага
                xrfRecord.Locked = flag;
                Xrf.WriteRecord(xrfRecord, false);
            }
        }

        /// <summary>
        /// ibatrak обновление статуса записи на актуализированный
        /// </summary>        
        public void SetRecordActualized(IrbisRecord record, bool keepLock, bool ifUpdate, bool padding)
        {
            if (record == null || record.Mfn <= 0)
                return;
            var deleted = record.Deleted;
            record.Status = RecordStatus.Last;
            if (deleted)
                record.Status |= RecordStatus.LogicallyDeleted;
            if (!ifUpdate)
                record.Status |= RecordStatus.NonActualized;
            XrfRecord xrfRecord = Xrf.ReadRecord(record.Mfn);
            Mst.UpdateRecordStatus(record.Status, xrfRecord.Offset);
            xrfRecord.Status = RecordStatus.AllZero;
            if (deleted)
                xrfRecord.Status |= RecordStatus.LogicallyDeleted;
            //оставить блокировку
            if (keepLock)
                xrfRecord.Status |= RecordStatus.Locked;
            //не было актуализации
            if (!ifUpdate)
                xrfRecord.Status |= RecordStatus.NonActualized;

            Xrf.WriteRecord(xrfRecord, padding);
            //в записи MST пишутся одни флаги, в XRF - другие
            //в результирующей записи нужно иметь комбинированный статус
            record.Status |= xrfRecord.Status;
        }

        /// <summary>
        /// ibatrak удаление записи
        /// </summary>
        public void DeleteRecord(IrbisRecord record, bool padding)
        {
            if (record.Mfn <= 0)
            {
                OnIrbis64Code(0);
                return;
            }
            //Mst.LockDatabase(true);
            XrfRecord xrfRecord = GetXrfRecordError(record.Mfn, RecordStatus.Locked | RecordStatus.Absent);
            if (_codeArgs.Code == 0 && !xrfRecord.Deleted)
            {
                long offset = xrfRecord.Offset;
                //предыдущие версии записи пометить как удаленные
                int version = Mst.ReadVersion(xrfRecord.Offset);
                record.Version = version + 1;
                record.PreviousOffset = xrfRecord.Offset;
                for (int i = 0; i < version; i++)
                {
                    Mst.UpdateRecordStatus(RecordStatus.LogicallyDeleted | RecordStatus.NonActualized, offset);
                    if (i < version - 1)
                    {
                        var leader = Mst.ReadRecordLeader(offset);
                        offset = leader.Previous;
                    }
                }

                offset = Mst.UpdateRecord(record, RecordStatus.Last | RecordStatus.LogicallyDeleted | RecordStatus.NonActualized, padding);
                xrfRecord.Offset = offset;
                xrfRecord.Status = RecordStatus.LogicallyDeleted | RecordStatus.NonActualized;
                Xrf.WriteRecord(xrfRecord, padding);
            }
            //Mst.LockDatabase(false);
            //в записи MST пишутся одни флаги, в XRF - другие
            //в результирующей записи нужно иметь комбинированный статус
            record.Status |= xrfRecord.Status;
        }

        /// <summary>
        /// ibatrak проверка записи
        /// </summary>
        private XrfRecord GetXrfRecordError(int mfn, RecordStatus status)
        {
            //при вызове GetMaxMfn перечитывается контрольная запись
            if (mfn <= 0 || mfn > GetMaxMfn())
            {
                OnIrbis64Code(-140 /*READ_WRONG_MFN*/);
                return null;
            }
            XrfRecord xrfRecord = null;
            try
            {
                xrfRecord = Xrf.ReadRecord(mfn);
            }
            catch (ArgumentOutOfRangeException)
            {
                OnIrbis64Code(-140 /*READ_WRONG_MFN*/);
                return null;
            }
            if ((xrfRecord.Status & RecordStatus.LogicallyDeleted & status) != 0)
            {
                OnIrbis64Code(-600 /*REC_DELETE*/);
                return xrfRecord;
            }
            if ((xrfRecord.Status & (RecordStatus.PhysicallyDeleted | RecordStatus.Absent) & status) != 0)
            {
                OnIrbis64Code(-601 /*REC_PHYS_DELETE*/);
                return xrfRecord;
            }
            if ((xrfRecord.Status & RecordStatus.Locked & status) != 0)
            {
                OnIrbis64Code(-602 /*ERR_RECLOCKED*/);
                return xrfRecord;
            }
            OnIrbis64Code(0);
            return xrfRecord;
        }

        /// <summary>
        /// ibatrak отмена удаления записи
        /// </summary>
        public void UndeleteRecord(IrbisRecord record, bool padding)
        {
            if (record.Mfn <= 0)
            {
                OnIrbis64Code(0);
                return;
            }
            //Mst.LockDatabase(true);
            XrfRecord xrfRecord = GetXrfRecordError(record.Mfn, RecordStatus.Locked | RecordStatus.PhysicallyDeleted);
            if (_codeArgs.Code == 0 && Convert.ToBoolean(xrfRecord.Status & RecordStatus.LogicallyDeleted))
            {
                long offset = xrfRecord.Offset;
                //снять отметку об удалении с предыдущих версий записи
                int version = Mst.ReadVersion(xrfRecord.Offset);
                record.Version = version + 1;
                record.PreviousOffset = xrfRecord.Offset;
                for (int i = 0; i < version; i++)
                {
                    Mst.UpdateRecordStatus(RecordStatus.NonActualized, offset);
                    if (i < version - 1)
                    {
                        var leader = Mst.ReadRecordLeader(offset);
                        offset = leader.Previous;
                    }
                }
                offset = Mst.UpdateRecord(record, RecordStatus.Last | RecordStatus.NonActualized, padding);
                xrfRecord.Offset = offset;
                xrfRecord.Status = RecordStatus.NonActualized;
                Xrf.WriteRecord(xrfRecord, padding);
            }
            //Mst.LockDatabase(false);
            //в записи MST пишутся одни флаги, в XRF - другие
            //в результирующей записи нужно иметь комбинированный статус
            record.Status |= xrfRecord.Status;
        }

        /// <summary>
        /// ibatrak инициализация базы данных
        /// </summary>
        public void InitDatabase()
        {
            Mst.Create();
            Xrf.Create();
            InvertedFile.Create();
        }

        //public IrbisRecord ReadRecord2
        //    (
        //        int mfn
        //    )
        //{
        //    XrfRecord xrfRecord = Xrf.ReadRecord(mfn);
        //    MstRecord mstRecord = Mst.ReadRecord2(xrfRecord.Offset);
        //    IrbisRecord result = mstRecord.DecodeRecord();
        //    result.Database = Database;
        //    return result;
        //}

        //public int[] SearchSimple(string key)
        //{
        //    int[] mfns = InvertedFile.SearchSimple(key);
        //    List<int> result = new List<int>();
        //    foreach (int mfn in mfns)
        //    {
        //        //ibatrak бывают отрицательные mfn
        //        //if (!Xrf.ReadRecord(mfn).Deleted)
        //        if (mfn > 0 && !Xrf.ReadRecord(mfn).Deleted)
        //        {
        //            result.Add(mfn);
        //        }
        //    }
        //    return result.ToArray();
        //}

        //public IrbisRecord[] SearchReadSimple(string key)
        //{
        //    int[] mfns = InvertedFile.SearchSimple(key);
        //    List<IrbisRecord> result = new List<IrbisRecord>();
        //    foreach (int mfn in mfns)
        //    {
        //        try
        //        {
        //            XrfRecord xrfRecord = Xrf.ReadRecord(mfn);
        //            if (!xrfRecord.Deleted)
        //            {
        //                IrbisRecord irbisRecord = Mst.ReadRecord(xrfRecord.Offset);
        //                if (!irbisRecord.Deleted)
        //                {
        //                    result.Add(irbisRecord);
        //                }
        //            }
        //        }
        //        catch (Exception ex)
        //        {
        //            //ibatrak вывод в лог
        //            //Debug.WriteLine(ex);
        //            var logger = LogManager.GetLogger(GetType());
        //            logger.Error("Ошибка поиска " + (key ?? ""), ex);
        //        }
        //    }
        //    return result.ToArray();
        //}

        public TermLink[] SearchExact(string key)
        {
            return InvertedFile.SearchExact(key);
        }

        public TermLink[] SearchExact(string key, int first, int limit)
        {
            return InvertedFile.SearchExact(key, first, limit);
        }

        public TermLink[] SearchStart(string key)
        {
            return InvertedFile.SearchStart(key);
        }

        public TermLink[] SearchRange(string keyA, string keyB)
        {
            return InvertedFile.SearchRange(keyA, keyB);
        }

        public SearchTermInfo SearchTermExact(string key)
        {
            return InvertedFile.SearchTermExact(key);
        }

        public SearchTermInfo[] SearchTermsStart(string key, int limit)
        {
            return InvertedFile.SearchTermsStart(key, limit);
        }

        public SearchTermInfo[] SearchTermsFrom(string key, bool searchBack, int limit)
        {
            return InvertedFile.SearchTermsFrom(key, searchBack, limit);
        }

        public TermLink[] GetTermLinks(SearchTermInfo term, int first, int limit)
        {
            return InvertedFile.GetTermLinks(term, first, limit);
        }

        #endregion

        #region IDisposable members

        public void Dispose()
        {
            if (Mst != null)
            {
                Mst.Dispose();
                Mst = null;
            }
            if (Xrf != null)
            {
                Xrf.Dispose();
                Xrf = null;
            }
            if (InvertedFile != null)
            {
                InvertedFile.Dispose();
                InvertedFile = null;
            }
        }

        #endregion
    }
}
