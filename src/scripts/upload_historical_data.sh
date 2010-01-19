#! /bin/bash

FILE_FOLDER="`pwd`/../ESP/ss/assets"

scp -r -P 8080 $FILE_FOLDER/*ILI* kyih@esphealth.org:~/ILI
scp -r -P 8080 $FILE_FOLDER/*AllEnc* kyih@esphealth.org:~/ILI
scp -r -P 8080 $FILE_FOLDER/* kyih@esphealth.org:~/other



