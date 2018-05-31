#ifndef CONTROLLER_H
#define CONTROLLER_H

#include "potential.hpp"
#include "state.hpp"

#include <Eigen/Dense>

#include <memory>

class ReconstructMesh;

/** @class AttitudeController

    @brief Attitude controller class 
    
    This class holds several functions to compute the desired attitude states
    of a vehicle

    @author Shankar Kulumani
    @version 31 May 2018
*/
class AttitudeController {
    friend class Controller;

    public:
        AttitudeController( void );
        virtual ~AttitudeController( void ) {};
        
        /** @fn void body_fixed_pointing_attitude(std::shared_ptr<const State> state_in)
                
            Find desired attitude states to point at the body

            @param state_in State shared pointer 
                pos - interial frame
                vel - vel of com in inertial frame
                R - sc body frame to inertial frame
                w - ang vel of sc wrt to inertial frame and in the body frame
            @returns None

            @author Shankar Kulumani
            @version 4 May 2018
        */
        void body_fixed_pointing_attitude(std::shared_ptr<const State> state_in);
        
        /** @fn void body_fixed_pointing_attitude(const double& time, const Eigen::Ref<const Eigen::VectorXd>& state_in)
                
            Overload to find attitude states to point at body

            @param time Current simulation time
            @param state_in 1x18 vector for the current state
                pos - interial frame
                vel - vel of com in inertial frame
                R - sc body frame to inertial frame
                w - ang vel of sc wrt to inertial frame and in the body frame
            @returns None

            @author Shankar Kulumani
            @version 4 May 2018
        */
        void body_fixed_pointing_attitude(const double& time, 
                const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state_in);

        // getters for the desired attitude state
        Eigen::Matrix<double, 3, 3> get_Rd() const; /**< SC Body to Inertial frame  */
        Eigen::Matrix<double, 3, 3> get_Rd_dot() const; /**< Derivative of SC body to inertial frame */
        Eigen::Matrix<double, 3, 1> get_ang_vel_d() const; /**< Ang vel of sc body wrt inertial frame in the sc body frame */
        Eigen::Matrix<double, 3, 1> get_ang_vel_d_dot() const; /**< Derivative of ang vel of sc in sc body frame */

    protected:
        Eigen::Matrix<double, 3, 3> mRd; /**< Desired rotation matrix - body to inertial frame */
        Eigen::Matrix<double, 3, 3> mRd_dot; /**< Desired rotation matrix derivative - body to inertial frame */
        Eigen::Matrix<double, 3, 1> mang_vel_d; /**< Desired angular velocity */
        Eigen::Matrix<double, 3, 1> mang_vel_d_dot; /**< Desired angular velocity derivative */ 
};

class TranslationController {
    friend class Controller; 
    
    private:
        Eigen::MatrixXd controller_vertices;
        Eigen::MatrixXi controller_faces;
        std::vector<Eigen::VectorXi> mesh_mapping;

        void generate_controller_mesh( void );
        void build_controller_mesh_mapping(std::shared_ptr<const MeshData> meshdata_ptr,
                                           const double& max_angle=0.53);

    public:
        TranslationController( void );
        virtual ~TranslationController( void ) {};
        
        // an extra constructor to initialize the matrices
        TranslationController(std::shared_ptr<const MeshData> meshdata_ptr,
                              const double& max_angle=0.53);

        void inertial_fixed_state(std::shared_ptr<const State> des_state);
        void inertial_fixed_state(const double& time, 
                const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state_in,
                const Eigen::Ref<const Eigen::Matrix<double, 1, 3> >& des_pos);
        /** @fn Compute desired translation state to minimize uncertainty
                
            Given the current state and the reconstructed mesh this will
            find the desired position, velocity, and acceleration to be 
            directly above the vertex with the maximum uncertainty.

            @param state State object defining the current state
            @param rmesh ReconstructMesh object with the v, f, and w 
            @returns void Desired state is saved to member variables

            @author Shankar Kulumani
            @version 22 April 2018
        */
        void minimize_uncertainty(std::shared_ptr<const State> state,
                                  std::shared_ptr<const ReconstructMesh> rmesh);
        void minimize_uncertainty(const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state,
                                  std::shared_ptr<const ReconstructMesh> rmesh);
        
        // Allow for input using an shared_ptr to asteroid
        void minimize_uncertainty(const double& t,
                                  std::shared_ptr<const State> state,
                                  std::shared_ptr<const ReconstructMesh> rmesh,
                                  std::shared_ptr<Asteroid> ast_est);
        void minimize_uncertainty(const double& t,
                                  const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state,
                                  std::shared_ptr<const ReconstructMesh> rmesh,
                                  std::shared_ptr<Asteroid> ast_est);

        Eigen::Matrix<double, 3, 1> get_posd( void ) const;
        Eigen::Matrix<double, 3, 1> get_veld( void ) const;
        Eigen::Matrix<double, 3, 1> get_acceld( void ) const;

        Eigen::MatrixXd get_controller_vertices( void ) const { return controller_vertices; }
        Eigen::MatrixXi get_controller_faces( void ) const { return controller_faces; }
        std::vector<Eigen::VectorXi> get_mesh_mapping( void ) const { return mesh_mapping; }
    protected:
        Eigen::Matrix<double, 3, 1> mposd;
        Eigen::Matrix<double, 3, 1> mveld;
        Eigen::Matrix<double, 3, 1> macceld;
};

class Controller: public TranslationController, public AttitudeController {
    public:
        Controller( void );
        virtual ~Controller( void ) {};

        Controller(std::shared_ptr<const MeshData> meshdata_ptr,
                const double& max_angle=0.2);

        void explore_asteroid(std::shared_ptr<const State> state, 
                std::shared_ptr<const ReconstructMesh> rmesh);
        void explore_asteroid(const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state,
                std::shared_ptr<const ReconstructMesh> rmesh);

        // TODO Need some unit tests for tese
        void explore_asteroid(const double& t,
                std::shared_ptr<const State> state,
                std::shared_ptr<const ReconstructMesh> rmesh,
                std::shared_ptr<Asteroid> ast_est);
        void explore_asteroid(const double& t,
                const Eigen::Ref<const Eigen::Matrix<double, 1, 18> >& state,
                std::shared_ptr<const ReconstructMesh> rmesh,
                std::shared_ptr<Asteroid> ast_est);
        /** @fn Output a state object with the desired state

          Output a state object with the desired state

          @returns state_ptr Pointer to a state object

          @author Shankar Kulumani
          @version 22 April 2018
          */ 
        std::shared_ptr<State> get_desired_state();       
};

// some extra functions for testing
double control_cost(const double& t,
                    const Eigen::Ref<const Eigen::Matrix<double, 1, 3> >& pos_des,
                    const std::shared_ptr<Asteroid> ast_est,
                    const double& m1=500, const double& m2=500,
                    const double& max_potential=1);

double integrate_control_cost(const double& t,
                              const Eigen::Ref<const Eigen::Matrix<double, Eigen::Dynamic, 3> >& waypoints,
                              const std::shared_ptr<Asteroid> ast_est);


#endif
