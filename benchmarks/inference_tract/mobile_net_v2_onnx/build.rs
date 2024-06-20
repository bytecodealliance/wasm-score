use std::process::Command;

fn main() {
    // Run the setup.sh to download the model
    let output = Command::new("bash")
        .arg("./setup.sh")
        .output()
        .expect("Failed to execute setup.sh");

    // Print the output of the download attempt
    if !output.stdout.is_empty() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    }

    // Check if the download was successful and print the error if not
    if output.status.success() {
        println!("setup.sh executed successfully");
        println!("cargo:note=setup.sh executed successfully.");
    } else {
        let error_message = String::from_utf8_lossy(&output.stderr);
        eprintln!("cargo:note=Failed to execute setup.sh: {}", error_message);
        eprintln!("Failed to execute setup.sh: {}", error_message);
        std::process::exit(1);
    }

    println!("cargo::rerun-if-changed=setup.sh");
}
