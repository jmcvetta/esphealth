/**
 * Bcdc_elrSoap.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package org.openuri.www;

public interface Bcdc_elrSoap extends java.rmi.Remote {
    public java.lang.String send_hl7_2X_xml_stream_batch(javax.activation.DataHandler dh) throws java.rmi.RemoteException;
    public java.lang.String send_hl7_2X_edi_batch(javax.activation.DataHandler dh) throws java.rmi.RemoteException;
    public java.lang.String send_smf_1X_batch(javax.activation.DataHandler dh) throws java.rmi.RemoteException;
    public java.lang.String send_ercc_hl7_2X_xml_stream_batch(javax.activation.DataHandler dh) throws java.rmi.RemoteException;
    public java.lang.String send_ercc_hl7_2X_edi_batch(javax.activation.DataHandler dh) throws java.rmi.RemoteException;
    public java.lang.String send_ercc_smf_1X_batch(javax.activation.DataHandler dh) throws java.rmi.RemoteException;
    public javax.activation.DataHandler recv_hl7_2X_xml_stream_batch(java.util.Calendar fromDate, java.util.Calendar toDate) throws java.rmi.RemoteException;
    public java.lang.String ack_recv_hl7_2X_xml_stream_batch(java.lang.String exportId) throws java.rmi.RemoteException;
    public javax.activation.DataHandler recv_ercc_smf_1X_batch(java.util.Calendar fromDate, java.util.Calendar toDate) throws java.rmi.RemoteException;
    public java.lang.String ack_recv_ercc_batch(java.lang.String exportId) throws java.rmi.RemoteException;
}
