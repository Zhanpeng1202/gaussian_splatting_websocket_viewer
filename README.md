# Websockect Remote Viewer for Gaussian Splatting

## Overview

This websocket viewer provide a light-weight, compact way to visualize for gaussian spalting remotely.
Windows / Linux user could visualize the training process through the SIBR viewer provided officially. While this websocket viewer is useful for Mac / server training.
Users can train 3dgs on a server and hope to view it on local computer.

## Setup

On the local computer

```shell
# download these file in local computer
git clone git@github.com:Zhanpeng1202/gaussian_splatting_websocket_viewer.git

# Connect Server with SSH with vscode
vscode ssh server 

#set up forward port in vscode
Terminal -> Ports -> Forward a Ports -> 6119
```

On the server

```shell
# clone the official gaussain splatting repository
git clone git@github.com:graphdeco-inria/gaussian-splatting.git --recursive

# put networkGUI_Websocket.py in to correct location inside the cloned repository
<location>
|---gaussian_splatting
|   |---gaussain_render
|   |   |---network_gui.py
|   |   |---network_gui_websocket.py

|   |---train.py 
# replace train.py with that provided in this repository
```

After we start training on the server, we open the render.html on local computer, we should be able to see the streaming for gaussain spaltting.

## Potential Lagging for Real-time Rendering

We might see some lagging when dragging rapidly, not in the gaussain splatting's real-time manner. Currently, it can be rendered **5 fps** in good network environment.
We tried to identify the issue, it seems to be located at the communication part between vscode forward process and local java script. If you know more information, we are more than happy to discuss with you.

-----------------------------
Code is built based on the Inria Gaussain Splatting repository(<https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/>) and the some other parts are provided by Bernhard Kerbl.
