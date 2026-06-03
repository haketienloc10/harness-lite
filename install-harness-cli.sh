cargo clean
cargo build --release -p harness-cli
cp target/release/harness-cli scripts/bin/harness-cli
