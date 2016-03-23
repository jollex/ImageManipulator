# ImageManipulator
In the process of migrating this to a web application.

# Program roadmap
```
Web Browser                  Server                    Script
   |                           |                         |
   | ----- Request to / -----> |                         |
Start page <--- HTML --------- |                         |
   |                           |                         |
Button press ----------------> |                         |
   |                   Request to /compute               |
   |                  with options parameter             |
   |                           |                         |
   |                  Calls script with CLI              |
   |                   arguments (blocking) -----------> |
   |                           |                 Creates images/GIF
   |                           |                         |
   |                           | <------------- Outputs list of files
Result page <- HTML -- Creates result page            created
   |                    using result files               |
   |                           |                         |
```
