// client.c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static int recv_all(int sock, void *buf, size_t len) {
    size_t total = 0;
    char *p = (char *)buf;

    while (total < len) {
        ssize_t n = recv(sock, p + total, len - total, 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) return -1;
        total += (size_t)n;
    }
    return 0;
}

static const char *media_player_for_file(const char *filename) {
    const char *ext = strrchr(filename, '.');
    if (!ext) return NULL;

    if (strcmp(ext, ".wav") == 0 || strcmp(ext, ".au") == 0) {
        return "aplay";
    }

    return "cvlc";
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "usage: %s <ip> <port> <output_file> <play_file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *ip = argv[1];
    int port = atoi(argv[2]);
    const char *output_file = argv[3];
    const char *play_file = argv[4];

    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    struct sockaddr_in server;
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons((uint16_t)port);

    if (inet_pton(AF_INET, ip, &server.sin_addr) <= 0) {
        fprintf(stderr, "invalid ip address\n");
        close(sock);
        return EXIT_FAILURE;
    }

    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("connect");
        close(sock);
        return EXIT_FAILURE;
    }

    long file_size = 0;
    if (recv_all(sock, &file_size, sizeof(file_size)) < 0) {
        fprintf(stderr, "failed to receive file size\n");
        close(sock);
        return EXIT_FAILURE;
    }

    FILE *out = fopen(output_file, "wb");
    