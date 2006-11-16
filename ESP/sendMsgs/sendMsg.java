

import java.io.*;
import java.rmi.*;
import javax.xml.rpc.*;
import org.openuri.www.*;
import org.apache.log4j.*;
import javax.activation.*;
import org.apache.axis.client.*;


public class sendMsg{

    private static Logger log = Logger.getLogger("sendMsg");


    public static void setAuth(Remote r, String user, String pw) {
        if(r == null) return;
        final org.apache.axis.client.Stub s = (org.apache.axis.client.Stub)r;
        s.setUsername(user);
        s.setPassword(pw);
    }


    public static String publishHl7Msg(String filename) {

        String response = "";
        String user="emr.upload.webservice";
        String pw="3mrUpw5vc!;!";

        try {

            Bcdc_elrLocator elr_svc = new Bcdc_elrLocator();
        	Bcdc_elrSoap elr_port = elr_svc.getbcdc_elrSoap();

            if (elr_port == null)
               return "SOAP Fault";


            setAuth(elr_port, user, pw);
            response = elr_port.send_hl7_2X_xml_stream_batch(new DataHandler(new FileDataSource(filename)));

       }
       catch (ServiceException se) {
             log.error("service exception: " +se.getMessage());
             response = "Service exception: " + se.getMessage();
       }
       catch (RemoteException re) {
		     log.error("remote exception: " +re.getMessage());
	         response = "Remote exception: " + re.getMessage();
       }

       return response;
    }




    public static void main(String args[]) throws Exception {

        String filename = args[0];
        System.err.println("In JAVA, Sending file: " + filename);
        String response = publishHl7Msg(filename);
        System.err.println("In JAVA, Remote Server Response: " +response);
        System.exit(0);

    }

}
