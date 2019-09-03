# SIT312_Group3
A device that enables travellers to share location and communicate in areas where there is no cell phone coverage.


End Node code
  
  The folder end-node contains a skeleton respository that demonstrates the end device code structure.
  
  end_node.py - the primary file that initiates the multhithreaded processing.
  
  andrew_wireless.py - the wireless functionality; Andrew is to place code here<br>
  benn_gps.py        - the gps retrieval function; Benn is to place code here<br>
  ian_ui.py          - the ui & display function;  Ian is to place code here<br>
  sarah_ui.py        - the audio functionality;    Sarah is to place code here<br>
  
  Demonstration:
    Clone respository (All files in end-node folder) and store in a common directory.
    Run end_node.py (Only Python3 has been verified thus far)
    
    Output:
      > python3 end_node.py
          Begin wireless     
          Begin ui
          UI: Hello from andrew_wireless.py
          End ui
          Begin gps
          Begin audio
          got audio
          End gps
          End audio
          GPS: 150.5,-45.4
          Message: SOS - Save our souls
          End wireless

          All running processes finished -------------------------------------
