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
        Output.text += "\n" + this.Comm.Host.Name + " > " + message;
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
        this.Comm.Host.SetPort(Port); // if client
        this.Comm.ListenPort = Port; // if server
        this.Comm.ForceReconnect();
        Output.text += string.Format("\nService Modification: {0}",
            (this.Comm.isServer) ? string.Format("Hosting on {0}", this.Comm.ListenPort) : string.Format("Connecting to {0}:{1}", this.Comm.Host.Address, this.Comm.Host.Port)
            );
    }

    public void ChangeAddress(string address)
    {
        this.Comm.Host.SetAddress(address);
        this.Comm.ForceReconnect();
        Output.text += string.Format("\nService Modification: {0}",
            (this.Comm.isServer) ? string.Format("Hosting on {0}", this.Comm.ListenPort) : string.Format("Connecting to {0}:{1}", this.Comm.Host.Address, this.Comm.Host.Port)
            );
    }

    public void ToggleServer(bool isClient)
    {
        this.Comm.isServer = !isClient;
        this.Comm.ForceReconnect();
        Output.text += string.Format("\nService Modification: {0}",
            (this.Comm.isServer) ? string.Format("Hosting on {0}", this.Comm.ListenPort) : string.Format("Connecting to {0}:{1}", this.Comm.Host.Address, this.Comm.Host.Port)
            );
    }
}
