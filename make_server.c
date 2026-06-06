// server.c
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static int send_all(int sock, const void *buf, size_t len) {
    size_t total = 0;
    const char *p = (const char *)buf;

    while (total < len) {
        ssize_t n = send(sock, p + total, len - total, 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (n == 0) return -1;
        total += (size_t)n;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s <port> <file>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int port = atoi(argv[1]);
    const char *file = argv[2];

    FILE *f = fopen(file, "rb");
    if (!f) {
        perror("fopen");
        return EXIT_FAILURE;
    }

    if (fseek(f, 0, SEEK_END) != 0) {
        perror("fseek");
        fclose(f);
        return EXIT_FAILURE;
    }

    long file_size = ftell(f);
    if (file_size < 0) {
        perror("ftell");
        fclose(f);
        return EXIT_FAILURE;
    }
    rewind(f);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        fclose(f);
        return EXIT_FAILURE;
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        fclose(f);
        return EXIT_FAILURE;
    }

    struct sockaddr_in address;
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons((uint16_t)port);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        fclose(f);
        return EXIT_FAILURE;
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen");
        close(server_fd);
        fclose(f);
        return EXIT_FAILURE;
    }

    printf("server listening on port %d\n", port);

    int client_fd = accept(server_fd, NULL, NULL);
    if (client_fd < 0) {
        perror("accept");
        close(server_fd);
        fclose(f);
        return EXIT_FAILURE;
    }

    if (send_all(client_fd, &file_size, sizeof(file_size)) < 0) {
        perror("send file size");
        close(client_fd);
        close(server_fd);
        fclose(f);
        return EXIT_FAILURE;
    }

    char buffer[4096];
    size_t n;
    while ((n = fread(buffer, 1, sizeof(buffer), f)) > 0) {
        if (send_all(client_fd, buffer, n) < 0) {
            perror("send file data");
            close(client_fd);
            close(server_fd);
            fclose(f);
            return EXIT_FAILURE;
        }
    }

    shutdown(client_fd, SHUT_WR);
    close(client_fd);
    close(server_fd);
    fclose(f);
    return EXIT_SUCCESS;
}