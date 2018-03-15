#include "loader.hpp"
#include "mesh.hpp"
#include "cgal.hpp"

#include "input_parser.hpp"

#include "stats.hpp"

#include <memory>

// try to write a function to  find distance from mesh to point using AABB
//
int main(int argc, char* argv[]) {
    InputParser input(argc, argv);
    if (input.option_exists("-h")) {
        std::cout << "Usage mesh -i input_file.obj" << std::endl;
    }

    const std::string input_file = input.get_command_option("-i");
    std::shared_ptr<MeshData> mesh;

    // create a mesh object
    if (!input_file.empty()) {
        mesh = Loader::load(input_file);
    }

    std::cout << "Vertices: \n" << mesh->vertices << std::endl;
    std::cout << "Faces: \n" << mesh->faces << std::endl;

    print_polyhedron_vertices(mesh);
    
    // lets try and build a surface mesh now
    
    surface_mesh_stats(mesh);
    print_surface_mesh_vertices(mesh);
    
    Eigen::Vector3d pt;
    pt << 2, 0, 0;
    distance_to_polyhedron(pt, mesh);
    return 0;
}
