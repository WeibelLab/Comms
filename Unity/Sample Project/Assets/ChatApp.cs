using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChatApp : MonoBehaviour
{
    public ReliableCommunication Comm;
    public UnityEngine.UI.Text Output;
    public UnityEngine.UI.Image Status;

    public void WriteMessage(string message)
    {
        Comm.Send(message);
        Output.text += "\nYou > " + message;
    }

    public void ReadResponse(string message)
    {
        Output.text += "\n"+this.Comm.Host.Name+" > " + message;
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
        this.Comm.Host = new CommunicationEndpoint(this.Comm.Host.Address, int.Parse(port), "My Friend");
        this.Comm.ForceReconnect();
    }

    public void ChangeAddress(string address) {
        this.Comm.Host = new CommunicationEndpoint(address, this.Comm.ListenPort, "My Friend");
        this.Comm.ForceReconnect();
    }

    public void ToggleServer(bool isClient)
    {
        this.Comm.isServer = !isClient;
        this.Comm.ForceReconnect();
    }
}
