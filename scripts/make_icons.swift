// Renders the menu-bar icons (template images: black on transparent).
//   swift scripts/make_icons.swift
import AppKit
import CoreText

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
let resources = root.appendingPathComponent("ModernMongolian.bundle/Contents/Resources")

struct Icon {
    let layoutName: String
    let text: String
    let fontName: String
    let vertical: Bool  // Mongolian script: rotate so the word stands upright
}

let icons = [
    Icon(layoutName: "Mongolian Modern Cyrillic", text: "Мн", fontName: "HelveticaNeue-Bold", vertical: false),
    Icon(layoutName: "Mongolian Traditional Script", text: "ᠮᠣ", fontName: "NotoSansMongolian", vertical: true),
]

func render(_ icon: Icon, pixels: Int) -> Data {
    let ctx = CGContext(data: nil, width: pixels, height: pixels, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    let side = CGFloat(pixels)
    func line(size: CGFloat) -> CTLine {
        let font = CTFontCreateWithName(icon.fontName as CFString, size, nil)
        let attrs: [NSAttributedString.Key: Any] = [.font: font, .foregroundColor: CGColor(gray: 0, alpha: 1)]
        return CTLineCreateWithAttributedString(NSAttributedString(string: icon.text, attributes: attrs))
    }
    // Fit the ink bounds into the square with a small margin.
    let probe = CTLineGetImageBounds(line(size: 100), ctx)
    let size = 100 * side * 0.9 / max(probe.width, probe.height)
    let l = line(size: size)
    let ink = CTLineGetImageBounds(l, ctx)
    ctx.translateBy(x: side / 2, y: side / 2)
    if icon.vertical { ctx.rotate(by: -.pi / 2) }  // clockwise: horizontal Mongolian lies on its side
    ctx.textPosition = CGPoint(x: -ink.midX, y: -ink.midY)
    CTLineDraw(l, ctx)
    let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)
    return rep.representation(using: .png, properties: [:])!
}

let fm = FileManager.default
for icon in icons {
    let iconset = fm.temporaryDirectory.appendingPathComponent("\(UUID().uuidString).iconset")
    try fm.createDirectory(at: iconset, withIntermediateDirectories: true)
    for (name, pixels) in [("16x16", 16), ("16x16@2x", 32), ("32x32", 32), ("32x32@2x", 64)] {
        try render(icon, pixels: pixels).write(to: iconset.appendingPathComponent("icon_\(name).png"))
    }
    let out = resources.appendingPathComponent("\(icon.layoutName).icns")
    let p = Process()
    p.executableURL = URL(fileURLWithPath: "/usr/bin/iconutil")
    p.arguments = ["-c", "icns", iconset.path, "-o", out.path]
    try p.run()
    p.waitUntilExit()
    try fm.removeItem(at: iconset)
    guard p.terminationStatus == 0 else { fatalError("iconutil failed for \(icon.layoutName)") }
    print("wrote \(out.path.replacingOccurrences(of: root.path + "/", with: ""))")
}
