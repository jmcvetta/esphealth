/**
 * Bcdc_elrLocator.java
 *
 * This file was auto-generated from WSDL
 * by the Apache Axis 1.4 Apr 22, 2006 (06:55:48 PDT) WSDL2Java emitter.
 */

package org.openuri.www;

public class Bcdc_elrLocator extends org.apache.axis.client.Service implements org.openuri.www.Bcdc_elr {

    public Bcdc_elrLocator() {
    }


    public Bcdc_elrLocator(org.apache.axis.EngineConfiguration config) {
        super(config);
    }

    public Bcdc_elrLocator(java.lang.String wsdlLoc, javax.xml.namespace.QName sName) throws javax.xml.rpc.ServiceException {
        super(wsdlLoc, sName);
    }

    // Use to get a proxy class for bcdc_elrSoap
    private java.lang.String bcdc_elrSoap_address = "https://d1elr.diagnosisone.com:443/ws/d1/bcdc_elr.jws";

    public java.lang.String getbcdc_elrSoapAddress() {
        return bcdc_elrSoap_address;
    }

    // The WSDD service name defaults to the port name.
    private java.lang.String bcdc_elrSoapWSDDServiceName = "bcdc_elrSoap";

    public java.lang.String getbcdc_elrSoapWSDDServiceName() {
        return bcdc_elrSoapWSDDServiceName;
    }

    public void setbcdc_elrSoapWSDDServiceName(java.lang.String name) {
        bcdc_elrSoapWSDDServiceName = name;
    }

    public org.openuri.www.Bcdc_elrSoap getbcdc_elrSoap() throws javax.xml.rpc.ServiceException {
       java.net.URL endpoint;
        try {
            endpoint = new java.net.URL(bcdc_elrSoap_address);
        }
        catch (java.net.MalformedURLException e) {
            throw new javax.xml.rpc.ServiceException(e);
        }
        return getbcdc_elrSoap(endpoint);
    }

    public org.openuri.www.Bcdc_elrSoap getbcdc_elrSoap(java.net.URL portAddress) throws javax.xml.rpc.ServiceException {
        try {
            org.openuri.www.Bcdc_elrSoapStub _stub = new org.openuri.www.Bcdc_elrSoapStub(portAddress, this);
            _stub.setPortName(getbcdc_elrSoapWSDDServiceName());
            return _stub;
        }
        catch (org.apache.axis.AxisFault e) {
            return null;
        }
    }

    public void setbcdc_elrSoapEndpointAddress(java.lang.String address) {
        bcdc_elrSoap_address = address;
    }

    /**
     * For the given interface, get the stub implementation.
     * If this service has no port for the given interface,
     * then ServiceException is thrown.
     */
    public java.rmi.Remote getPort(Class serviceEndpointInterface) throws javax.xml.rpc.ServiceException {
        try {
            if (org.openuri.www.Bcdc_elrSoap.class.isAssignableFrom(serviceEndpointInterface)) {
                org.openuri.www.Bcdc_elrSoapStub _stub = new org.openuri.www.Bcdc_elrSoapStub(new java.net.URL(bcdc_elrSoap_address), this);
                _stub.setPortName(getbcdc_elrSoapWSDDServiceName());
                return _stub;
            }
        }
        catch (java.lang.Throwable t) {
            throw new javax.xml.rpc.ServiceException(t);
        }
        throw new javax.xml.rpc.ServiceException("There is no stub implementation for the interface:  " + (serviceEndpointInterface == null ? "null" : serviceEndpointInterface.getName()));
    }

    /**
     * For the given interface, get the stub implementation.
     * If this service has no port for the given interface,
     * then ServiceException is thrown.
     */
    public java.rmi.Remote getPort(javax.xml.namespace.QName portName, Class serviceEndpointInterface) throws javax.xml.rpc.ServiceException {
        if (portName == null) {
            return getPort(serviceEndpointInterface);
        }
        java.lang.String inputPortName = portName.getLocalPart();
        if ("bcdc_elrSoap".equals(inputPortName)) {
            return getbcdc_elrSoap();
        }
        else  {
            java.rmi.Remote _stub = getPort(serviceEndpointInterface);
            ((org.apache.axis.client.Stub) _stub).setPortName(portName);
            return _stub;
        }
    }

    public javax.xml.namespace.QName getServiceName() {
        return new javax.xml.namespace.QName("http://www.openuri.org/", "bcdc_elr");
    }

    private java.util.HashSet ports = null;

    public java.util.Iterator getPorts() {
        if (ports == null) {
            ports = new java.util.HashSet();
            ports.add(new javax.xml.namespace.QName("http://www.openuri.org/", "bcdc_elrSoap"));
        }
        return ports.iterator();
    }

    /**
    * Set the endpoint address for the specified port name.
    */
    public void setEndpointAddress(java.lang.String portName, java.lang.String address) throws javax.xml.rpc.ServiceException {
        
if ("bcdc_elrSoap".equals(portName)) {
            setbcdc_elrSoapEndpointAddress(address);
        }
        else 
{ // Unknown Port Name
            throw new javax.xml.rpc.ServiceException(" Cannot set Endpoint Address for Unknown Port" + portName);
        }
    }

    /**
    * Set the endpoint address for the specified port name.
    */
    public void setEndpointAddress(javax.xml.namespace.QName portName, java.lang.String address) throws javax.xml.rpc.ServiceException {
        setEndpointAddress(portName.getLocalPart(), address);
    }

}
