#include "state.hpp"

#include <Eigen/Dense>

#include <memory>

State::State( void ) {
    mpos.setZero(3);
    mvel.setZero(3);
    mR.setIdentity(3, 3);
    mang_vel.setZero(3);
    
    maccel.setZero(3);
    mR_dot.setZero(3, 3);
    mang_vel_dot.setZero(3);

    mtime = 0;
    state_to_array();
}

State::State(const double& time_in, const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state_array) {
    // set all the member variables
    mpos.setZero(3);
    mpos(0) = state_array(0); 
    mpos(1) = state_array(1);
    mpos(2) = state_array(2);

    mvel.setZero(3);
    mvel(0) = state_array(3);
    mvel(1) = state_array(4);
    mvel(2) = state_array(5);

    mR.setZero(3, 3);
    mR(0, 0) = state_array(6);
    mR(0, 1) = state_array(7);
    mR(0, 2) = state_array(8);
    mR(1, 0) = state_array(9);
    mR(1, 1) = state_array(10);
    mR(1, 2) = state_array(11);
    mR(2, 0) = state_array(12);
    mR(2, 1) = state_array(13);
    mR(2, 2) = state_array(14);

    mang_vel.setZero(3);
    mang_vel(0) = state_array(15);
    mang_vel(1) = state_array(16);
    mang_vel(2) = state_array(17);

    mtime = time_in;
    state_to_array();
}

// Definitions for getters of member variables
Eigen::Vector3d State::get_pos( void ) const {
    return mpos;
}

Eigen::Vector3d State::get_vel( void ) const {
    return mvel;
}

Eigen::Matrix<double, 3, 3> State::get_att( void ) const {
    return mR;
}

Eigen::Vector3d State::get_ang_vel( void ) const {
    return mang_vel;
}

Eigen::Matrix<double, 1, 18> State::get_state( void ) const {
    return mstate;
}

Eigen::Vector3d State::get_accel( void ) const {
    return maccel;
}

Eigen::Vector3d State::get_ang_vel_dot( void ) const {
    return mang_vel_dot;
}

Eigen::Matrix<double, 3, 3> State::get_att_dot( void ) const {
    return mR_dot;
}

double State::get_time( void  ) const {
    return mtime;
}

void State::state_to_array() {
    // add postion to the array
    mstate(0) = mpos(0);
    mstate(1) = mpos(1);
    mstate(2) = mpos(2);

    // add velocity to array
    mstate(3) = mvel(0);
    mstate(4) = mvel(1);
    mstate(5) = mvel(2);

    // add rotation matrix to state array
    mstate(6) = mR(0, 0);
    mstate(7) = mR(0, 1);
    mstate(8) = mR(0, 2);
    mstate(9) = mR(1, 0);
    mstate(10) = mR(1, 1);
    mstate(11) = mR(1, 2);
    mstate(12) = mR(2, 0);
    mstate(13) = mR(2, 1);
    mstate(14) = mR(2, 2);

    // add angular velocity
    mstate(15) = mang_vel(0);
    mstate(16) = mang_vel(1);
    mstate(17) = mang_vel(2);
}

void State::update_state(std::shared_ptr<State> new_state) {
    mpos = new_state->get_pos();
    mvel = new_state->get_vel();
    maccel = new_state->get_accel();

    mR = new_state->get_att();
    mR_dot = new_state->get_att_dot();

    mang_vel = new_state->get_ang_vel();
    mang_vel_dot = new_state->get_ang_vel_dot();

    // update teh controller varaibles too
    
    state_to_array();

}
