# CSC568

Distributed File Systerm with encryption & deduplicated backup

Project description:
Implement a distributed file system that allows users to transfer files between client and server. When files are upoaded, the backup side also stores the files. Besides, we want to add certain features regarding security and effectiveness to make the system even more stable and reliable to maintain information availability and integrity.


Deliverables:

1. Security:

(1) Access control：
The file uploaded by the client can be set to have a password. When other clients want to download the file, they need to provide the correct password to start downloading.

(2) Encryption:
With the password client provides, the files are encrypted. On server side, the encrypted files cannot be read. Only when the password is provided, the files can be downloaded and read.  

(3) Record of operations:
Our system also includes a log file that records the operations of the users to the system. It includes which file is uploaded or uploaded by which client, and the address and port of that client.


2. Deduplication:
Simply tell if two files are the same based on the filename is not reliable, so we need to look into the content. For simplification, we could first compare the size of the two files. If two files have the same size, then compare the hash value of the files. If the hash valuesa are the same, build a symbolic link to link the two files.


3. Dependencies:
Ubuntu 18.04  
FUSE 3.4.1



