# Workflowista

An proof-of-concept for communication between Workflow for iOS and Pythonista for iOS.

```
    >>> server = PythonistaServer()
    >>> output = server.run('Client')
    >>> output
    [{'greeting': 'Hello'}]
```

## Pythonista's Perspective

It is a single python file, `workflowista.py`. Open it up and run the Pythonista unit tests (hold the play button and pick 'Run Unit Tests'. The script should start a server, `PythonistaServer`, fire up flask in it's `Receiver`, and open Workflow with it's url scheme using it's `Transmitter`. 


## Workflow's Perspective

In Workflow, make a workflow called 'Client' that creates a URL for 'http://localhost:5000' and uses 'Get Contents of URL.' This is how Workflow passes data to Pythonista. Change the **Method** to POST and the **Request Body** to JSON. You can then put the data in the headers. For the test to pass, give it one key 'greeting` with a value 'Hello'. The 'Client' workflow I used is in this repo.

## Installation

### Pythonista

Download the zip from [GitHub](https://github.com/davidseibert/workflowista), use the 'Run Python Script' extension for Pythonista, and select 'Import File'. 

### After you download it to Pythonista, select the 'Client.wflow' file in the Library and share to Workflow to import it.