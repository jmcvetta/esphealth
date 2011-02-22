#
#                                                               
#  Scirpt mhslespftp.sh is called from daily schedule job that  
#  extracts epic data to upload to the esp server               
#                                                               
#  Created  09/05/09: M. Burton                                 
#
echo ==== start of script ====
echo
date
# 
#
esp_env=/epic/emt
esp_dir=$esp_env/mb
esp_archive=$esp_dir/esparchive
Local_dir=$esp_dir
echo Local Directory= $esp_dir
#
# remove previous FTP transfer status files
#
if test -f $esp_dir/ftp_transfer_status.txt
   then
   rm $esp_dir/ftp_transfer_status.txt
fi
#
#
if test -f $esp_dir/chkftp_complete.txt
   then
   rm $esp_dir/chkftp_complete.txt
fi
#
if test -f $esp_dir/chkftp_sent.txt
   then
   rm $esp_dir/chkftp_sent.txt
fi
#
##############################################################
ftp_Server=999.999.999.999                                      
ftp_Login=userid
ftp_Password=password
ftp -n -v $ftp_Server <<EndFTP > $esp_dir/ftp_transfer_status.txt
            user $ftp_Login $ftp_Password
            lcd $Local_dir
            prompt
            mput epic*.esp.*
            quit                        
EndFTP
# 
grep "command succesful" $esp_dir/ftp_transfer_status.txt > $esp_dir/chkftp_complete.txt
grep "bytes sent" $esp_dir/ftp_transfer_status.txt > $esp_dir/chkftp_sent.txt
if test ! -s $esp_dir/chkftp_sent.txt
then
	echo "From mhepic3 to esp data was not transferred correctly or bad connection, please try script again ..."
        echo "From mhepic3 to esp FTP Unsuccessful. Please notify Integration On-call person." | mailx -s "esp FTP was Unsuccessful mhslespftp.sh" "user@hospital.org"
   exit
fi
# 
# Move retrieved files to archvie
##############################################################
chmod a=rw $esp_dir\/epic*.esp.*
mv $esp_dir/epic*.esp.* $esp_archive/
echo "Completed FTP to esp "
#
echo
echo ====  end of script  ====
