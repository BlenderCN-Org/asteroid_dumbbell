"""Equations of motion of a dumbbell 

"""
from dynamics import controller
import numpy as np
from kinematics import attitude

def eoms_controlled_relative_blender_ode(t, state, dum, ast):
    """Relative EOMS defined in the rotating asteroid frame

    This function defines the motion of a dumbbell spacecraft in orbit around
    an asteroid.
    The EOMS are defined relative to the asteroid itself, which is in a state
    of constant rotation.
    You need to use this function with scipy.integrate.ode class
    This is setup to test Blender using a fixed asteroid

    Inputs:
        t - current time of simulation (sec)
        state - (18,) relative state of dumbbell with respect to asteroid
            pos - state[0:3] in km position of the dumbbell with respect to the
            asteroid and defined in the asteroid fixed frame
            vel - state[3:6] in km/sec is the velocity of dumbbell wrt the
            asteroid and defined in the asteroid fixed frame
            R - state[6:15] rotation matrix which converts vectors from the
            dumbbell frame to the asteroid frame
            w - state[15:18] rad/sec angular velocity of the dumbbell wrt
            inertial frame and defined in the asteroid frame
        ast - asteroid object

    Output:
        state_dot - (18,) derivative of state. The order is the same as the input state.
    """
    
    # unpack the state
    pos = state[0:3] # location of the COM of dumbbell in asteroid fixed frame
    vel = state[3:6] # vel of com wrt to asteroid expressed in the asteroid fixed frame
    R = np.reshape(state[6:15],(3,3)) # sc body frame to asteroid body frame R = R_A^T R_1
    w = state[15:18] # angular velocity of sc wrt inertial frame and expressed in asteroid fixed frame

    Ra = attitude.rot3(ast.omega*t, 'c') # asteroid body frame to inertial frame

    # unpack parameters for the dumbbell
    m1 = dum.m1
    m2 = dum.m2
    m = m1 + m2
    J = dum.J
    Jr = R.dot(J).dot(R.T)
    Wa = ast.omega*np.array([0,0,1]) # angular velocity vector of asteroid

    # the position of each mass in the dumbbell body frame
    rho1 = dum.zeta1
    rho2 = dum.zeta2

    # position of each mass in the asteroid frame
    z1 = pos + R.dot(rho1)
    z2 = pos + R.dot(rho2)

    z = pos # position of COM in asteroid frame

    # compute the potential at this state
    (U1, U1_grad, U1_grad_mat, U1laplace) = ast.polyhedron_potential(z1)
    (U2, U2_grad, U2_grad_mat, U2laplace) = ast.polyhedron_potential(z2)

    # force due to each mass expressed in asteroid body frame
    F1 = m1*U1_grad
    F2 = m2*U2_grad

    M1 = m1*attitude.hat_map(R.dot(rho1)).dot(U1_grad) 
    M2 = m2*attitude.hat_map(R.dot(rho2)).dot(U2_grad) 
    
    des_tran_tuple = controller.asteroid_circumnavigate(t, 3600, 1)
    des_att_tuple = controller.asteroid_pointing(t, state, ast)

    u_f = controller.translation_controller_asteroid(t, state, F1 + F2,
                                                     dum, ast, des_tran_tuple)
    u_m = controller.attitude_controller_asteroid(t, state, M1 + M2, 
                                                  dum, ast, des_att_tuple)

    # state derivatives
    pos_dot = vel - attitude.hat_map(Wa).dot(pos)
    vel_dot = 1/m * (F1 + F2 - m * attitude.hat_map(Wa).dot(vel) + u_f)
    # vel_dot = 1/m * (F_com) 
    R_dot = attitude.hat_map(w).dot(R) - attitude.hat_map(Wa).dot(R)
    R_dot = R_dot.reshape(9)
    w_dot = np.linalg.inv(Jr).dot(M1 + M2 - Jr.dot(attitude.hat_map(Wa)).dot(w) + u_m)
    state_dot = np.hstack((pos_dot, vel_dot, R_dot, w_dot))
    
    return state_dot

def eoms_controlled_inertial_circumnavigate(t, state, dum, ast, tf, loops):
    """Inertial dumbbell equations of motion about an asteroid 
    
    This method must be used with the scipy.integrate.ode class instead of the
    more convienent scipy.integrate.odeint. In addition, we can control the
    dumbbell given full state feedback. Blender is used to generate imagery
    during the simulation.

    Inputs:
        t - Current simulation time step
        state - (18,) array which defines the state of the vehicle 
            pos - (3,) position of the dumbbell with respect to the
            asteroid center of mass and expressed in the inertial frame
            vel - (3,) velocity of the dumbbell with respect to the
            asteroid center of mass and expressed in the inertial frame
            R - (9,) attitude of the dumbbell with defines the
            transformation of a vector in the dumbbell frame to the
            inertial frame ang_vel - (3,) angular velocity of the dumbbell
            with respect to the inertial frame and represented in the
            dumbbell frame
        ast - Asteroid class object holding the asteroid gravitational
        model and other useful parameters
    """
    # unpack the state
    pos = state[0:3] # location of the center of mass in the inertial frame
    vel = state[3:6] # vel of com in inertial frame
    R = np.reshape(state[6:15],(3,3)) # sc body frame to inertial frame
    ang_vel = state[15:18] # angular velocity of sc wrt inertial frame defined in body frame

    Ra = attitude.rot3(ast.omega*t, 'c') # asteroid body frame to inertial frame

    # unpack parameters for the dumbbell
    J = dum.J

    rho1 = dum.zeta1
    rho2 = dum.zeta2

    # position of each mass in the asteroid frame
    z1 = Ra.T.dot(pos + R.dot(rho1))
    z2 = Ra.T.dot(pos + R.dot(rho2))

    z = Ra.T.dot(pos) # position of COM in asteroid frame

    # compute the potential at this state
    (U1, U1_grad, U1_grad_mat, U1laplace) = ast.polyhedron_potential(z1)
    (U2, U2_grad, U2_grad_mat, U2laplace) = ast.polyhedron_potential(z2)

    F1 = dum.m1*Ra.dot(U1_grad)
    F2 = dum.m2*Ra.dot(U2_grad)

    M1 = dum.m1 * attitude.hat_map(rho1).dot(R.T.dot(Ra).dot(U1_grad))
    M2 = dum.m2 * attitude.hat_map(rho2).dot(R.T.dot(Ra).dot(U2_grad))
    
    # generate image at this current state only at a specifc time
    # blender.driver(pos, R, ast.omega * t, [5, 0, 1], 'test' + str.zfill(str(t), 4))
    # use the imagery to figure out motion and pass to the controller instead
    # of the true state

    # calculate the desired attitude and translational trajectory
    des_att_tuple = controller.body_fixed_pointing_attitude(t, state)
    des_tran_tuple = controller.inertial_circumnavigate(t, tf, loops)
    # input trajectory and compute the control inputs
    # compute the control input
    u_m = controller.attitude_controller(t, state, M1+M2, dum, ast, des_att_tuple)
    u_f = controller.translation_controller(t, state, F1+F2, dum, ast, des_tran_tuple)

    pos_dot = vel
    vel_dot = 1/(dum.m1+dum.m2) *(F1 + F2 + u_f)
    R_dot = R.dot(attitude.hat_map(ang_vel)).reshape(9)
    ang_vel_dot = np.linalg.inv(J).dot(-np.cross(ang_vel,J.dot(ang_vel)) + M1 + M2 + u_m)

    statedot = np.hstack((pos_dot, vel_dot, R_dot, ang_vel_dot))

    return statedot

def eoms_controlled_inertial_lissajous(t, state, dum, ast, tf, loops):
    """Inertial dumbbell equations of motion about an asteroid 
    
    This method must be used with the scipy.integrate.ode class instead of the
    more convienent scipy.integrate.odeint. In addition, we can control the
    dumbbell given full state feedback. Blender is used to generate imagery
    during the simulation.

    Inputs:
        t - Current simulation time step
        state - (18,) array which defines the state of the vehicle 
            pos - (3,) position of the dumbbell with respect to the
            asteroid center of mass and expressed in the inertial frame
            vel - (3,) velocity of the dumbbell with respect to the
            asteroid center of mass and expressed in the inertial frame
            R - (9,) attitude of the dumbbell with defines the
            transformation of a vector in the dumbbell frame to the
            inertial frame ang_vel - (3,) angular velocity of the dumbbell
            with respect to the inertial frame and represented in the
            dumbbell frame
        ast - Asteroid class object holding the asteroid gravitational
        model and other useful parameters
    """
    # unpack the state
    pos = state[0:3] # location of the center of mass in the inertial frame
    vel = state[3:6] # vel of com in inertial frame
    R = np.reshape(state[6:15],(3,3)) # sc body frame to inertial frame
    ang_vel = state[15:18] # angular velocity of sc wrt inertial frame defined in body frame

    Ra = attitude.rot3(ast.omega*t, 'c') # asteroid body frame to inertial frame

    # unpack parameters for the dumbbell
    J = dum.J

    rho1 = dum.zeta1
    rho2 = dum.zeta2

    # position of each mass in the asteroid frame
    z1 = Ra.T.dot(pos + R.dot(rho1))
    z2 = Ra.T.dot(pos + R.dot(rho2))

    z = Ra.T.dot(pos) # position of COM in asteroid frame

    # compute the potential at this state
    (U1, U1_grad, U1_grad_mat, U1laplace) = ast.polyhedron_potential(z1)
    (U2, U2_grad, U2_grad_mat, U2laplace) = ast.polyhedron_potential(z2)

    F1 = dum.m1*Ra.dot(U1_grad)
    F2 = dum.m2*Ra.dot(U2_grad)

    M1 = dum.m1 * attitude.hat_map(rho1).dot(R.T.dot(Ra).dot(U1_grad))
    M2 = dum.m2 * attitude.hat_map(rho2).dot(R.T.dot(Ra).dot(U2_grad))
    
    # generate image at this current state only at a specifc time
    # blender.driver(pos, R, ast.omega * t, [5, 0, 1], 'test' + str.zfill(str(t), 4))
    # use the imagery to figure out motion and pass to the controller instead
    # of the true state

    # calculate the desired attitude and translational trajectory
    des_att_tuple = controller.body_fixed_pointing_attitude(t, state)
    des_tran_tuple = controller.inertial_lissajous_yz_plane(t, tf, loops)
    # input trajectory and compute the control inputs
    # compute the control input
    u_m = controller.attitude_controller(t, state, M1+M2, dum, ast, des_att_tuple)
    u_f = controller.translation_controller(t, state, F1+F2, dum, ast, des_tran_tuple)

    pos_dot = vel
    vel_dot = 1/(dum.m1+dum.m2) *(F1 + F2 + u_f)
    R_dot = R.dot(attitude.hat_map(ang_vel)).reshape(9)
    ang_vel_dot = np.linalg.inv(J).dot(-np.cross(ang_vel,J.dot(ang_vel)) + M1 + M2 + u_m)

    statedot = np.hstack((pos_dot, vel_dot, R_dot, ang_vel_dot))

    return statedot

def eoms_controlled_inertial_quarter_equatorial(t, state, dum, ast, tf, loops):
    """Inertial dumbbell equations of motion about an asteroid 
    
    This method must be used with the scipy.integrate.ode class instead of the
    more convienent scipy.integrate.odeint. In addition, we can control the
    dumbbell given full state feedback. Blender is used to generate imagery
    during the simulation.

    Inputs:
        t - Current simulation time step
        state - (18,) array which defines the state of the vehicle 
            pos - (3,) position of the dumbbell with respect to the
            asteroid center of mass and expressed in the inertial frame
            vel - (3,) velocity of the dumbbell with respect to the
            asteroid center of mass and expressed in the inertial frame
            R - (9,) attitude of the dumbbell with defines the
            transformation of a vector in the dumbbell frame to the
            inertial frame ang_vel - (3,) angular velocity of the dumbbell
            with respect to the inertial frame and represented in the
            dumbbell frame
        ast - Asteroid class object holding the asteroid gravitational
        model and other useful parameters
    """
    # unpack the state
    pos = state[0:3] # location of the center of mass in the inertial frame
    vel = state[3:6] # vel of com in inertial frame
    R = np.reshape(state[6:15],(3,3)) # sc body frame to inertial frame
    ang_vel = state[15:18] # angular velocity of sc wrt inertial frame defined in body frame

    Ra = attitude.rot3(ast.omega*t, 'c') # asteroid body frame to inertial frame

    # unpack parameters for the dumbbell
    J = dum.J

    rho1 = dum.zeta1
    rho2 = dum.zeta2

    # position of each mass in the asteroid frame
    z1 = Ra.T.dot(pos + R.dot(rho1))
    z2 = Ra.T.dot(pos + R.dot(rho2))

    z = Ra.T.dot(pos) # position of COM in asteroid frame

    # compute the potential at this state
    (U1, U1_grad, U1_grad_mat, U1laplace) = ast.polyhedron_potential(z1)
    (U2, U2_grad, U2_grad_mat, U2laplace) = ast.polyhedron_potential(z2)

    F1 = dum.m1*Ra.dot(U1_grad)
    F2 = dum.m2*Ra.dot(U2_grad)

    M1 = dum.m1 * attitude.hat_map(rho1).dot(R.T.dot(Ra).dot(U1_grad))
    M2 = dum.m2 * attitude.hat_map(rho2).dot(R.T.dot(Ra).dot(U2_grad))
    
    # generate image at this current state only at a specifc time
    # blender.driver(pos, R, ast.omega * t, [5, 0, 1], 'test' + str.zfill(str(t), 4))
    # use the imagery to figure out motion and pass to the controller instead
    # of the true state

    # calculate the desired attitude and translational trajectory
    des_att_tuple = controller.body_fixed_pointing_attitude(t, state)
    des_tran_tuple = controller.inertial_quarter_equatorial_plane(t, tf, loops)
    # input trajectory and compute the control inputs
    # compute the control input
    u_m = controller.attitude_controller(t, state, M1+M2, dum, ast, des_att_tuple)
    u_f = controller.translation_controller(t, state, F1+F2, dum, ast, des_tran_tuple)

    pos_dot = vel
    vel_dot = 1/(dum.m1+dum.m2) *(F1 + F2 + u_f)
    R_dot = R.dot(attitude.hat_map(ang_vel)).reshape(9)
    ang_vel_dot = np.linalg.inv(J).dot(-np.cross(ang_vel,J.dot(ang_vel)) + M1 + M2 + u_m)

    statedot = np.hstack((pos_dot, vel_dot, R_dot, ang_vel_dot))

    return statedot