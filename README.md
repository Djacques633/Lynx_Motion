# Lynx_Motion
Code I worked with in my Summer of 2019 to design a 4 Degree of Freedom (DOF) Motion Table

* This code won't do anything standalone, as it requires various pieces of hardware in order to operate.
* In action, this utilized 4 different Lynx Smart Servos, various STM32 Bluepill boards, and 3-D printed parts to create a rotating table where we could control the height, pitch, roll, and the yaw of the table. There was also an IMU where we could control the table with motion controls.
* Files:
  - IMU: The code to take the IMU readings into the bluepill and send it off to the computer where it was recieved by the python script
  - Lynxtable: Processed the code from the IMU and calculated the readings in terms of 4 angles that were sent to Lynx_Motion_Table. Also had various other functions that we played around with to create different patterns of rotations.
  - Lynx_Motion_Table: Took the angles from the Python script and sent those to the respective servos. Also delt with a lot of timing problems to create a smoother rotation.
