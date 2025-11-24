// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "SwiftEngine",
    platforms: [
        .macOS(.v11)
    ],
    products: [
        .executable(name: "SwiftEngine", targets: ["SwiftEngine"])
    ],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
    ],
    targets: [
        // Targets are the basic building blocks of a package.
        .executableTarget(
            name: "SwiftEngine",
            dependencies: []),
    ]
)
