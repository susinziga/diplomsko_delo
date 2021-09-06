if(action == old_action):
                if(action == 1):
                    steps, queue_length_current, waiting_time_current = simulate1_1(steps , green_duration, max_steps)
                    sum_queue_length += queue_length_current
                   
                    '''
                    traci.trafficlight.setPhase ('TL', 1)
                    steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                    sum_waiting_time += waiting_time_current
                    sum_queue_length += queue_length_current
                    '''
                if(action == 0):
                    steps, queue_length_current, waiting_time_current = simulate0_0(steps , green_duration, max_steps)
                    sum_queue_length += queue_length_current
                   
                    '''
                    traci.trafficlight.setPhase ('TL', 0)
                    steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                    sum_waiting_time += waiting_time_current
                    sum_queue_length += queue_length_current
                    '''
            
            
            if(action == 0 and action != old_action):
                steps, queue_length_current, waiting_time_current = simulate_0(steps , green_duration, max_steps)
                sum_queue_length += queue_length_current
            
                '''
                traci.trafficlight.setPhase('TL', 5)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 6)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 7)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase ('TL', 0)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                '''
                


            if(action == 1 and action != old_action):
                steps, queue_length_current, waiting_time_current = simulate_1(steps , green_duration, max_steps)
                sum_queue_length += queue_length_current
              
                '''
                traci.trafficlight.setPhase('TL', 1)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 2)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase('TL', 3)
                steps, queue_length_current, waiting_time_current = _simulate(steps , yellow_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                traci.trafficlight.setPhase ('TL', 4)
                steps, queue_length_current, waiting_time_current = _simulate(steps , green_duration, max_steps)
                sum_waiting_time += waiting_time_current
                sum_queue_length += queue_length_current
                '''