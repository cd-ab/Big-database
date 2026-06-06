#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <linux/limits.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <stdint.h>
#include <signal.h>

#define MAX_LINE 1024
#define MAX_ARGS 64

int main(){
char line[MAX_LINE];
char *args[MAX_ARGS];




//piping func
void exec_pipeline(char *left, char *right){
  int pipefd[2];
  pid_t pid1, pid2;
//left side of the pipe, first child
  if(pipe(pipefd)==-1){
    perror("pipe");
    return;
  }

  pid1=fork();
  if(pid1==0){
    close(pipefd[0]);//close read end
    dup2(pipefd[1], STDOUT_FILENO);
    //stdout pipe write
    close(pipefd[1]);//close original write
    char *args1[10];
    execlp(strtok(left, " "),
    strtok(left, " "), NULL);
    perror("execvpe left");
    exit(127);
  }else{
    close(pipefd[1]);
  }

  pid2=fork();
  if(pid2==0){
    dup2(pipefd[0], STDIN_FILENO);
    close(pipefd[0]);
    char *args2[10];
    execlp(strtok(right, " "),
    strtok(right, " "), NULL);
    perror("execvp right");
    exit(127);
  }

        

  //parent close both ends and wait

  close(pipefd[0]);
  close(pipefd[1]);
  int status;
  waitpid(pid1, &status, 0);
  waitpid(pid2, &status, 0);
}


//signal handler

//void handle_sigint(int sig){
 // write(1, "\ncaught ctrl-c shell alive.\n$", 30);
//}
//cwd
char *path(){  
char cwd[PATH_MAX];
if(getcwd(cwd, sizeof(cwd)) !=NULL){
  printf("\033[0;32m[%s]", cwd);
}else{
  perror("\033[0;31m getcwd error");
}
fflush(stdout);
return 0;

}

void handle_sigint(int sig){
  write(1, "\n", 2);
  path();
}
//cd
void cd(){
  if(args[1]==NULL){
        fprintf(stderr, "\033[0;31m cd to where");
      }else{
         if(chdir(args[1]) != 0){
          perror("\033[0;31m pyshell");
        }
     }
    
      }
//get path for stat
char *which(const char *cmd){
  char *path = getenv("PATH");
  if(!path) return NULL;

  char *p = strtok(strdup(path), ":");
  while(p){
    size_t len = strlen(p) + strlen(cmd) + 2;
    char *buf = malloc(len);
    snprintf(buf, len, "%s/%s", p, cmd);
    if(access(buf, X_OK)==0){
      return buf;
    }
    free(buf);
    p=strtok(NULL, ":");
  }
  return NULL;
}
 

//resource monitor func
void what_i_used(){
  struct rusage usage;
  int resource;

  if(resource=getrusage(RUSAGE_SELF, &usage) ==-1){
    perror("\033[0;31m getrusage error");

}else{
  printf("user_time : %ld.%06ld\n", usage.ru_utime.tv_sec, usage.ru_utime.tv_usec);
  printf("MAX RSS: %ldkbs\n", usage.ru_maxrss);

  }
}
//the main loop
  while(1){
    path();
    if(!fgets(line, sizeof(line), stdin))break;
    line[strcspn(line, "\n")] =0;
    if(strlen(line) == 0)continue;
    char *left =strtok(line, "|");
    char *right = strtok(NULL, "|");

    int i =0;
     args[i] =strtok(line, " ");
    while(args[i] !=NULL && i < MAX_ARGS-1){
      args[++i] = strtok(NULL, " ");
    }
    
    args[i]=NULL;
    if(args[0] == NULL)continue;
    if(strcmp(args[0], "exit") == 0) break;
    if(strcmp(args[0], "cd")==0){
      cd();
    }

    //file metadata
    void dynamic( ){
      char *dir=path();
      char *full_path = which(*args);
      if(!full_path){
        printf("command %s: not found in $PATH\n", args[0]);
        return;
      }
      struct stat sb;
      if(lstat(full_path,  &sb) == -1){
        perror("lstat");
        free(full_path);
        exit(127);
      }
      printf("PROGRAM INFO:     ");
      switch(sb.st_mode & S_IFMT){
        case S_IFBLK: printf("\033[0;36m this is a block device\n");break;
        case S_IFCHR: printf("\033[0;36m program in execution is a character device\n");break;        case S_IFDIR: printf("\033[0;36m welcome to directory %s", dir);break;
        case S_IFREG :printf("\033[0;36m the program in execution is a regular file\n");break;
        default :printf("\033[0;31m unknown file type");break;

        }
      printf("filesize : %jd by bytes\n", (intmax_t) sb.st_size);
      return;
     }

    //signal func call
    struct sigaction sa;
    sa.sa_handler = &handle_sigint;//point to our handler function
    sa.sa_flags =SA_RESTART;//restart syscalls
    sigemptyset(&sa.sa_mask);//dont block any other signals
    if(sigaction(SIGINT,&sa, NULL)==-1){
        perror("sigaction");
        return 1;
        }


      
   //resource monitor 
   if(strcmp(args[0], "eats")==0){
     what_i_used();
   } 
   //cmdline executor
   void term(){
    pid_t pid = fork();
    if(pid<0){
      perror("\033[0;31m fork failed");
    }else if(pid == 0){
      if(execvp(args[0], args)==-1){
        perror("\033[0;31m command not found");
      }exit(127);
    }
    else {

      wait(NULL);
    }
  }
   if(right==NULL){
     dynamic();
     usleep(10000);
     term();
   }
   exec_pipeline(left, right);

  
  }
  return 0;
}
