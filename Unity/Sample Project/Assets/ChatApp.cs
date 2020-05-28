using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChatApp : MonoBehaviour
{
    [SerializeField]
    public ReliableCommunication RComm;
    [SerializeField]
    public UnreliableCommunication UComm;
    public UnityEngine.UI.Text Output;
    public UnityEngine.UI.Image Status;

    public void WriteMessage(string message)
    {
        RComm.Send(message);
        UComm.SendTo(message, UComm.Targets[0].AsIPEndPoint());
        Output.text += "\n<color=#ffffffbb>You > " + message+"</color>";
    }

    public void ReadUnreliableResponse(string message)
    {
        Output.text += "\n<color=#ffff00ff>" + this.UComm.Targets[0].Name + " > " + message + "</color>";
    }

    public void ReadReliableResponse(string message)
    {
        Output.text += "\n<color=#00ffffff>" + this.RComm.Host.Name + " > " + message + "</color>";
    }

    public void OnConnect(ReliableCommunication Client)
    {
        this.Status.color = new Color(0, 1, 0);
    }

    public void OnDisconnect(ReliableCommunication Client)
    {
        this.Status.color = new Color(1, 0, 0);
    }

    public void ChangePort(string port)
    {
        int Port = int.Parse(port);
        this.RComm.Host.SetPort(Port); // if client
        this.RComm.ListenPort = Port; // if server
        this.RComm.ForceReconnect();
        Output.text += string.Format("\nTCP Service Modification: {0}",
            (this.RComm.isServer) ? string.Format("Hosting on {0}", this.RComm.ListenPort) : string.Format("Connecting to {0}:{1}", this.RComm.Host.Address, this.RComm.Host.Port)
            );
    }

    public void ChangeUdpPort(string port)
    {
        int Port = int.Parse(port);
        this.UComm.port = Port;
        this.UComm.RestartServer();
        Output.text += string.Format("\nUDP Service Modification: listening on {0}", this.UComm.port);
    }

    public void ChangeUdpTargetPort(string port)
    {
        string addr = this.UComm.Targets[0].Address;
        string name = this.UComm.Targets[0].Name;
        this.UComm.Targets = new List<CommunicationEndpoint>();
        this.UComm.Targets.Add(new CommunicationEndpoint(addr, int.Parse(port), name));
        Output.text += string.Format("\nUDP Service Modification: sending to {0}:{1}", this.UComm.Targets[0].Address, this.UComm.Targets[0].Port);
    }

    public void ChangeAddress(string address)
    {
        this.RComm.Host.SetAddress(address);
        this.RComm.ForceReconnect();
        Output.text += string.Format("\nTCP Service Modification: {0}",
            (this.RComm.isServer) ? string.Format("Hosting on {0}", this.RComm.ListenPort) : string.Format("Connecting to {0}:{1}", this.RComm.Host.Address, this.RComm.Host.Port)
            );
    }

    public void ChangeUdpTargetAddress(string address)
    {
        int port = this.UComm.Targets[0].Port;
        string name = this.UComm.Targets[0].Name;
        this.UComm.Targets = new List<CommunicationEndpoint>();
        this.UComm.Targets.Add(new CommunicationEndpoint(address, port, name));
        Output.text += string.Format("\nUDP Service Modification: sending to {0}:{1}", this.UComm.Targets[0].Address, this.UComm.Targets[0].Port);
    }

    public void ToggleServer(bool isClient)
    {
        this.RComm.isServer = !isClient;
        this.RComm.ForceReconnect();
        Output.text += string.Format("\nService Modification: {0}",
            (this.RComm.isServer) ? string.Format("Hosting on {0}", this.RComm.ListenPort) : string.Format("Connecting to {0}:{1}", this.RComm.Host.Address, this.RComm.Host.Port)
            );
    }

    public void ClearChat()
    {
        Output.text = "";
    }
}
