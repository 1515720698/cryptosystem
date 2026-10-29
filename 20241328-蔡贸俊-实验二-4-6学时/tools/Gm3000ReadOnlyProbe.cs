using System;
using System.Runtime.InteropServices;

internal static class Gm3000ReadOnlyProbe
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
    private struct TokenInfo
    {
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)] public byte[] Label;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)] public byte[] Manufacturer;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)] public byte[] Model;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)] public byte[] Serial;
        public UInt32 Flags;
        public UInt32 MaxSessionCount;
        public UInt32 SessionCount;
        public UInt32 MaxRwSessionCount;
        public UInt32 RwSessionCount;
        public UInt32 MaxPinLength;
        public UInt32 MinPinLength;
        public UInt32 TotalPublicMemory;
        public UInt32 FreePublicMemory;
        public UInt32 TotalPrivateMemory;
        public UInt32 FreePrivateMemory;
        public byte HardwareMajor;
        public byte HardwareMinor;
        public byte FirmwareMajor;
        public byte FirmwareMinor;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)] public byte[] UtcTime;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetDllDirectory(string path);
    [DllImport("gm3000_pkcs11.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern UInt32 C_Initialize(IntPtr initArgs);
    [DllImport("gm3000_pkcs11.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern UInt32 C_Finalize(IntPtr reserved);
    [DllImport("gm3000_pkcs11.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern UInt32 C_GetSlotList(byte tokenPresent, IntPtr slotList, ref UInt32 count);
    [DllImport("gm3000_pkcs11.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern UInt32 C_GetTokenInfo(UInt32 slotId, out TokenInfo info);

    private static string Text(byte[] value)
    {
        return System.Text.Encoding.ASCII.GetString(value).Trim(' ', '\0');
    }

    private static int Main(string[] args)
    {
        if (args.Length != 1) { Console.Error.WriteLine("usage: Gm3000ReadOnlyProbe <vendor-dll-directory>"); return 2; }
        if (!SetDllDirectory(args[0])) { Console.Error.WriteLine("Cannot set DLL directory"); return 2; }
        UInt32 rv = C_Initialize(IntPtr.Zero);
        if (rv != 0) { Console.Error.WriteLine("C_Initialize=0x{0:X8}", rv); return 1; }
        try
        {
            UInt32 count = 0;
            rv = C_GetSlotList(1, IntPtr.Zero, ref count);
            if (rv != 0) { Console.Error.WriteLine("C_GetSlotList(count)=0x{0:X8}", rv); return 1; }
            IntPtr slots = Marshal.AllocHGlobal(checked((int)count * 4));
            try
            {
                rv = C_GetSlotList(1, slots, ref count);
                if (rv != 0) { Console.Error.WriteLine("C_GetSlotList(values)=0x{0:X8}", rv); return 1; }
                Console.WriteLine("token_present_slots={0}", count);
                for (int i = 0; i < count; i++)
                {
                    UInt32 slot = unchecked((UInt32)Marshal.ReadInt32(slots, i * 4));
                    TokenInfo info;
                    rv = C_GetTokenInfo(slot, out info);
                    if (rv != 0) { Console.WriteLine("slot={0} token_info_rv=0x{1:X8}", slot, rv); continue; }
                    Console.WriteLine("slot={0} label={1} manufacturer={2} model={3} serial={4} flags=0x{5:X8}", slot, Text(info.Label), Text(info.Manufacturer), Text(info.Model), Text(info.Serial), info.Flags);
                }
            }
            finally { Marshal.FreeHGlobal(slots); }
        }
        finally { C_Finalize(IntPtr.Zero); }
        return 0;
    }
}
