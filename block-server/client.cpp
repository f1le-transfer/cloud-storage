#include <stdio.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <unistd.h> 
#include <string.h>
#include <bits/stdc++.h>
using namespace std;

//macro definitions
#define PORT 5050
#define MAX_MESSAGE_LEN 60  // Maximum len of message from client can't be more than 60
#define HEADER 64

int main(int argc, char const *argv[]) {
    int sock = 0, valread;
    struct sockaddr_in serv_addr; 
    char msg[MAX_MESSAGE_LEN];
    char buffer[4096] = {0};

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
        printf("\n Socket creation error \n");
        return -1;
    }
   
    serv_addr.sin_family = AF_INET; 
    serv_addr.sin_port = htons(PORT); 
       
    // Convert IPv4 and IPv6 addresses from text to binary form 
    if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        printf("\nInvalid address/ Address not supported \n"); 
        return -1; 
    } 
   
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) { 
        printf("\nConnection Failed \n"); 
        return -1; 
    }
    
    
    // Input
    printf("msg? ");
    cin.getline(msg, MAX_MESSAGE_LEN);
    
    
    // Send header to server *here*
    send(sock, "Some message", strlen("Some message"), 0);
    
    send(sock, msg, strlen(msg), 0 );
    
    shutdown(sock, 2);
    return 0;
}
