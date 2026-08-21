// List photos on a USB-connected iPhone via ImageCaptureCore.
// Usage: swift iphone_photos.swift list            -> prints inventory TSV
//        swift iphone_photos.swift import <dir>    -> downloads all items to <dir>
import Foundation
import ImageCaptureCore

let mode = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "list"
let destDir = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "/tmp/iphone_import"

class Delegate: NSObject, ICDeviceBrowserDelegate, ICCameraDeviceDelegate, ICCameraDeviceDownloadDelegate {
    var camera: ICCameraDevice?
    var pending = 0
    var downloadQueue: [ICCameraFile] = []

    func deviceBrowser(_ browser: ICDeviceBrowser, didAdd device: ICDevice, moreComing: Bool) {
        guard let cam = device as? ICCameraDevice, camera == nil else { return }
        camera = cam
        cam.delegate = self
        cam.requestOpenSession()
    }
    func deviceBrowser(_ browser: ICDeviceBrowser, didRemove device: ICDevice, moreGoing: Bool) {}
    func device(_ device: ICDevice, didOpenSessionWithError error: Error?) {
        if let error = error { FileHandle.standardError.write("open error: \(error)\n".data(using: .utf8)!); exit(1) }
    }
    func device(_ device: ICDevice, didCloseSessionWithError error: Error?) {}
    func didRemove(_ device: ICDevice) {}
    func cameraDevice(_ camera: ICCameraDevice, didAdd items: [ICCameraItem]) {}
    func cameraDevice(_ camera: ICCameraDevice, didRemove items: [ICCameraItem]) {}
    func cameraDevice(_ camera: ICCameraDevice, didReceiveThumbnail thumbnail: CGImage?, for item: ICCameraItem, error: (any Error)?) {}
    func cameraDevice(_ camera: ICCameraDevice, didReceiveMetadata metadata: [AnyHashable: Any]?, for item: ICCameraItem, error: (any Error)?) {}
    func cameraDevice(_ camera: ICCameraDevice, didRenameItems items: [ICCameraItem]) {}
    func cameraDeviceDidChangeCapability(_ camera: ICCameraDevice) {}
    func cameraDevice(_ camera: ICCameraDevice, didReceivePTPEvent eventData: Data) {}
    func cameraDeviceDidRemoveAccessRestriction(_ device: ICDevice) {}
    func cameraDeviceDidEnableAccessRestriction(_ device: ICDevice) {}

    func deviceDidBecomeReady(withCompleteContentCatalog device: ICCameraDevice) {
        let items = (device.mediaFiles?.isEmpty == false ? device.mediaFiles : device.contents) ?? []
        let fmt = ISO8601DateFormatter()
        var files: [ICCameraFile] = []
        for item in items { collect(item, into: &files) }
        if mode == "list" {
            print("name\tsize_bytes\tcreated\ttype")
            for f in files {
                let date = f.creationDate.map { fmt.string(from: $0) } ?? "?"
                print("\(f.name ?? "?")\t\(f.fileSize)\t\(date)\t\(f.uti ?? "?")")
            }
            device.requestCloseSession()
            exit(0)
        } else {
            try? FileManager.default.createDirectory(atPath: destDir, withIntermediateDirectories: true)
            downloadQueue = files
            pending = files.count
            if pending == 0 { exit(0) }
            for f in files {
                device.requestDownloadFile(f, options: [.downloadsDirectoryURL: URL(fileURLWithPath: destDir)],
                                           downloadDelegate: self, didDownloadSelector: #selector(didDownload(_:error:options:contextInfo:)), contextInfo: nil)
            }
        }
    }
    func collect(_ item: ICCameraItem, into files: inout [ICCameraFile]) {
        if let f = item as? ICCameraFile { files.append(f) }
        if let folder = item as? ICCameraFolder { for c in folder.contents ?? [] { collect(c, into: &files) } }
    }
    @objc func didDownload(_ file: ICCameraFile, error: Error?, options: [String: Any], contextInfo: UnsafeMutableRawPointer?) {
        pending -= 1
        if let error = error { print("FAIL \(file.name ?? "?"): \(error.localizedDescription)") }
        else { print("OK \(file.name ?? "?")") }
        if pending == 0 { camera?.requestCloseSession(); exit(0) }
    }
}

let delegate = Delegate()
let browser = ICDeviceBrowser()
browser.delegate = delegate
browser.browsedDeviceTypeMask = ICDeviceTypeMask(rawValue: ICDeviceTypeMask.camera.rawValue | ICDeviceLocationTypeMask.local.rawValue)!
browser.start()
RunLoop.main.run(until: Date(timeIntervalSinceNow: 600))
FileHandle.standardError.write("timeout\n".data(using: .utf8)!)
exit(2)
