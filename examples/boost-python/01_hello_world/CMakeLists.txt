PYTHON_ADD_MODULE(hello hello.cpp)
FILE(COPY hello.py DESTINATION .)
ADD_TEST(NAME 01_hello_world COMMAND ${PYTHON_EXECUTABLE} hello.py)
