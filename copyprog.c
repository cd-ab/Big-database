#include <stdio.h>

#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <stdint.h>
#include <fcntl.h>

#define handle_error(msg)\
  do {perror(msg);exit(EXIT_FAILURE);} while(0)

int main(int argc, char *argv[]){
  struct stat sf;

  void v_flag(){
   while(lstat(argv[1], &sf) ==-1){
      handle_error("lstat");
    }
  printf("successfully copied  %s to %s by %jd bytes\n",argv[1], argv[2], (intmax_t)sf.st_size);
}

    void h_flag(){
    printf("tiny cp clone, usage: gcopy <source> <dest> <flags>\n -h  print this help message\n -v  verbose\n");
    exit(127);
    }
    
if(argc<2){
 h_flag();
  }

 int input=open(argv[1], O_RDONLY);
  if(!input){
    handle_error("input");
  }
  //syscall open for output file //
  int fd= open(argv[2], O_WRONLY| O_CREAT | O_TRUNC, sf.st_mode);
  if(!fd){
    handle_error("fd");
  
  }

int opt;
while((opt=getopt(argc, argv, "h:v")) !=-1){
  switch(opt){
    case 'h':
      h_flag();
      break;
    case 'v':
      v_flag();
      break;

    default:
      int b=optind;

    }
}

  // convert fd to FILE with syscall wrapper//
  /*FILE *convert_fd=fdopen(fd, "wb");
  if(!convert_fd){
    handle_error("fdopen");
    close(fd);
    fclose(input);
    return 1;
  }*/
//copy in 4KB buffered chunks//

off_t blk = sf.st_blksize;
char *buf=malloc(blk);
if(buf==NULL){
  handle_error("buf");
}
  
ssize_t nread;
while(nread=read(input, buf, blk)){
  if(write(fd ,buf, nread) != nread){
    handle_error("fwrite");
  }

}
free(buf);
//cleanup
close(input);
close(fd);


return 0;
}
