# AWS File Sharing

A simple solution for sharing files securely using AWS services.

## Features

- Upload and download files
- Secure file storage with AWS S3
- User authentication (optional)
- Easy setup and deployment

## Prerequisites

- [Node.js](https://nodejs.org/)
- [AWS CLI](https://aws.amazon.com/cli/)
- AWS account with S3 access

## Setup

1. Clone the repository:
  ```bash
  git clone https://github.com/yourusername/AWSFileSharing.git
  cd AWSFileSharing
  ```

2. Install dependencies:
  ```bash
  npm install
  ```

3. Configure AWS credentials:
  ```bash
  aws configure
  ```

4. Update configuration in `config.js` with your S3 bucket details.

## Usage

- **Upload a file:**
  ```bash
  node upload.js <filepath>
  ```

- **Download a file:**
  ```bash
  node download.js <filename>
  ```

## License

MIT License