// Локальне розпізнавання тексту (Apple Vision, українська + англійська) для сортування картинок.
// Використання: swift scripts/classtime/ocr.swift список_шляхів.txt > результат.jsonl
// Вихід -- рядок JSON на картинку: {"path": "...", "text": "..."}
import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1, let list = try? String(contentsOfFile: args[1], encoding: .utf8) else {
    FileHandle.standardError.write("вкажіть файл зі списком шляхів\n".data(using: .utf8)!); exit(1)
}
for path in list.split(separator: "\n").map(String.init) where !path.isEmpty {
    var text = ""
    if let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let req = VNRecognizeTextRequest()
        req.recognitionLevel = .accurate
        req.recognitionLanguages = ["uk-UA", "en-US"]
        req.usesLanguageCorrection = true
        try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
        text = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
    }
    let obj: [String: String] = ["path": path, "text": text]
    if let d = try? JSONSerialization.data(withJSONObject: obj), let s = String(data: d, encoding: .utf8) { print(s) }
}
