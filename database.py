# Some contructor data for the program

margin_error           = 500        #ms
horizontally_move_time = 800      #ms
rotation_move_time     = 1200    #ms
rotation_move_half_time=rotation_move_time/2
pick_move_time         = 400 #ms
pick_move_half_time    = pick_move_time/2

size                   = (20,20)    #cases
max_move               = horizontally_move_time + rotation_move_time



period_10_fps          = 100 #ms
movement_step          = horizontally_move_time/period_10_fps #horizontally_move_time/period_10_fps