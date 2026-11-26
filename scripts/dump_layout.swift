// Print, as JSON, what an installed keyboard layout types for key codes 0-127
// under each modifier state, as compiled and interpreted by macOS itself.
//   swift scripts/dump_layout.swift <input source id> <name>=<modifier state>...
import Carbon
import Foundation

let args = CommandLine.arguments.dropFirst()
guard let id = args.first else { fatalError("usage: dump_layout.swift <input source id> name=state...") }
let states = args.dropFirst().map { arg -> (String, UInt32) in
    let parts = arg.split(separator: "=")
    return (String(parts[0]), UInt32(parts[1])!)
}

let filter = [kTISPropertyInputSourceID as String: id] as CFDictionary
guard let sources = TISCreateInputSourceList(filter, true)?.takeRetainedValue() as? [TISInputSource],
      let source = sources.first,
      let raw = TISGetInputSourceProperty(source, kTISPropertyUnicodeKeyLayoutData)
else {
    FileHandle.standardError.write("input source \(id) is not installed\n".data(using: .utf8)!)
    exit(1)
}
let data = Unmanaged<CFData>.fromOpaque(raw).takeUnretainedValue() as Data

var result: [String: [String: String]] = [:]
data.withUnsafeBytes { bytes in
    let layout = bytes.baseAddress!.assumingMemoryBound(to: UCKeyboardLayout.self)
    for (name, state) in states {
        var table: [String: String] = [:]
        for code in UInt16(0)..<128 {
            var dead: UInt32 = 0
            var length = 0
            var chars = [UniChar](repeating: 0, count: 16)
            UCKeyTranslate(layout, code, UInt16(kUCKeyActionDown), state, UInt32(LMGetKbdType()),
                           OptionBits(kUCKeyTranslateNoDeadKeysBit), &dead, chars.count, &length, &chars)
            table[String(code)] = String(utf16CodeUnits: chars, count: length)
        }
        result[name] = table
    }
}
FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys]))
