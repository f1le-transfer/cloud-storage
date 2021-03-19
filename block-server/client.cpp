#include <iostream>
#include <fstream>
#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>

using namespace std;

class Client_socket {
    fstream file;
    
    int PORT;
    int general_socket_descriptor;
    struct sockaddr_in address;
    int address_length;
    
    public:
        Client_socket() {
            create_socket();
            PORT = 5050;
            
            address.sin_family = AF_INET;
            address.sin_port = htons(PORT);
            address_length = sizeof(address);
            
            if (inet_pton(AF_INET, "127.0.0.1", &address.sin_addr) <= 0) {
                cout << "[ERROR] : Invalid address\n";
            }
            
            create_connection();
            
            file.open("./test.txt", ios::in | ios::binary);
            if (file.is_open()) {
                cout << "[LOG] : File is ready to Transmit.\n";
            }
            else {
                cout << "[ERROR] : File loading failed, Exititng.\n";
                exit(EXIT_FAILURE);
            }
        }
    
    void create_socket() {
        if ((general_socket_descriptor = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            perror("[ERROR] : Socket failed.\n");
            exit(EXIT_FAILURE);
        }
        cout << "[LOG] : Socket Created Successfully.\n";
    }
    
    void create_connection() {
        if (connect(general_socket_descriptor, (struct sockaddr *)&address, sizeof(address)) < 0) {
            perror("[ERROR] : connection attempt failed.\n");
            exit(EXIT_FAILURE);
        }
        cout << "[LOG] : Connection Successfull.\n";
    }
    
    void receive_file() {
        char buffer[4096] = {};
        int valread = read(general_socket_descriptor , buffer, 4096);
        cout << "[LOG] : Data received " << valread << " bytes\n";
        cout << "[LOG] : Saving data to file.\n";
        
        file << buffer;
        cout << "[LOG] : File Saved.\n";
    }
    
    void transmit_file() {
        std::string contents((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
        cout << "[LOG] : Transmission Data Size " << contents.length() << " Bytes.\n";

        cout<<"[LOG] : Sending...\n";

        int bytes_sent = send(general_socket_descriptor , contents.c_str() , contents.length() , 0 );
        cout << "[LOG] : Transmitted Data Size " << bytes_sent << " Bytes.\n";

        cout << "[LOG] : File Transfer Complete.\n";
        
        close_connection();
    }
    
    void close_connection() {
        cout << "[LOG] : Closing connection...\n";
        shutdown(general_socket_descriptor, 2);
        cout << "[LOG] : Connection closed.\n";
    }
};


int send_file() {
    Client_socket C;
    C.transmit_file();
    return 0;
};

int recv_file() {
    Client_socket C;
    C.receive_file();
    return 0;
};

int main() {
    send_file();
    return 0;
}
