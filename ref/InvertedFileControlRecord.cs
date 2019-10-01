using System;
using System.Runtime.InteropServices;

namespace ManagedClient
{
    /// <summary>
    /// ibatrak Контрольная запись инвертного файла
    /// </summary>
    [Serializable]
    [StructLayout(LayoutKind.Sequential)]
    public class InvertedFileControlRecord
    {
        /// <summary>
        /// Размер управляющей записи.
        /// </summary>        
        public const int RecordSize = 20;

        /// <summary>
        /// Ссылка на свободное место в ifp файле
        /// </summary>
        public long IfpOffset { get; set; }

        /// <summary>
        /// Количество блоков в N01 файле
        /// </summary>
        public int NodeBlockCount { get; set; }

        /// <summary>
        /// Количество блоков в L01 файле
        /// </summary>
        public int LeafBlockCount { get; set; }

        /// <summary>
        /// Резерв
        /// </summary>
        public int Reserv { get; set; }
    }
}
