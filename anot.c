#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]){
if(argc < 3){
  printf("use -h for help");
  return 1;
}
  int help=0;
  for(int i=0; i<argc;i++){
    if(strcmp(argv[i], "-h") == 0){
      help=1;
      printf("copy prog again, usage: ./copyprog <input> <output>");
    }
  }
  struct stat st;

  if(stat(argv[1], &st) ==-1){
    perror("file prolly doesnt exist\n");
    return 1;
  }
  if(!S_ISREG(st.st_mode)){
    fprintf(stderr , "%s is not a regular file", argv[1]);
    return 1;
  }

  int src_fd=open(argv[1], O_RDONLY);
  int dest_fd= open(argv[2], O_CREAT |O_WRONLY| O_TRUNC, st.st_mode);

  if(!src_fd || !dest_fd){
    perror("bad file descriptors");
    return 1;
  }

  size_t blksize = st.st_blksize;
  char *buf= malloc(blksize);
  if(buf==NULL){
    perror("malloc failed");
    return 1;
  }

size_t nread;
while(nread=read(src_fd, buf, blksize)){
    if(write(dest_fd, buf, nread) !=nread){
    perror("read and write failed miserably");
    break;
    }
    }
free(buf);
close(src_fd);
close(dest_fd);
return 0;
}

