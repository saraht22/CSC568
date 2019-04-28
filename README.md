# CSC568

[![LICENSE](https://img.shields.io/badge/license-Anti%20996-blue.svg?style=flat-square)](https://github.com/996icu/996.ICU/blob/master/LICENSE)

WORM with some new features

Project description:
Implement a write once read many file system that allows users to make the filesystem and read data from it. Data is written when creating the filesystem and can’t be changed later. Besides, we want to add certain features regarding security and effectiveness to make the system even more stable and reliable to maintain information availability and integrity.


Deliverables:

1. Security:

(1) Access control：
With WORM system, we can control the writing permission to the system. But reading can also leak information sometimes. One could read the file and write to another location that can be accessed by others.
Our assumption is that we give the file an extra attribute, to store the process name that can access the file. Each time a process access the file, the program checks the attribute with the process name. If matched, then read permission given.

(2) Encryption:
Nowadays the popular encryption algorithm AES-GCM provides the protection of both the confidentiality and integrity of files that is, without the key, one cannot read the original file and with the key, one can verify whether the file has been changed or not.
Record of access:
WORM system needs to record every access action from different users, including access user name and action time. In some situations, we need to read records for solving security problems or do rollback operations. Thus, we need this feature to help us.


2. Deduplication:
Simply tell if two files are the same based on the filename is not reliable, so we need to look into the content. For simplification, we could first compare the size of the two files. If the same, then split the file into chunks and hashes each chunk with a big hash. Each file’s contents are stored as a list of hashes. Here we use a flat table to store the hashes and the data they belong to, and keep a reference count to know when to free an entry. If hashes match, data matches, then replace this with a reference to the matching data. Else, It’s new data, store it.


3. Dependencies:
Ubuntu 18.04  
FUSE 3.4.1

4. File Design:

(1) master.c:  
Part of the operations before building the WORM file system, including deduplication, encryption and Access control. 
Given a folder, first we scan all the files in the folder, saving their size. If two files are of the same size, then compare their hash value to see if they are duplicate files. If so, only save one of them. Then, take the password parameter from the user input to encrypt the whole system.

(2) worm.c:    
Inplementation of read-only control on the generated file system built by master.


