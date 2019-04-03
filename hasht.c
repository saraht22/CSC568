#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

#define DUPE_COUNT_INIT 5

typedef struct filenode 
{
  char file_name [256];
  size_t file_size; 
  char hash_list [1000]; 
  struct filenode *next;
} filenode;

typedef struct dunode 
{
  size_t size;
  char hash_list [1000];
  struct dunode *next;
  short int num_dus;
  short int num_alloc;
  filenode* duplicates [DUPE_COUNT_INIT];
} dunode;


dunode* duwalker;

char *programName;
char directory [1000];
int prompt;

signed int build_du_list (filenode *fname, size_t fsize, dunode *du);
signed int initialize (dunode *du);
signed int operation ();
signed int hash_func (dunode *du, char *filename);

void usage ();

signed int build_du_list (filenode *fname, size_t fsize, dunode *du)
{
  if (du->size != fsize)
    return -1; /* because something went screwy */

  if (du->num_dus == du->num_alloc) { /* realloc array */
    void *_tmp = realloc (du, sizeof (struct dunode) + du->num_alloc);
    if (_tmp == NULL) {
      fprintf (stderr, "Unable to resize duplicates struct\n");
      return -1;
    }
    du->num_alloc *= 2;
    du = _tmp;
  }
  du->duplicates[du->num_dus++] = fname;
  return 0;
}

signed int initialize (dunode *du)
{
  du->num_alloc = 5;
  du->num_dus = 0;
  return 0;
}

signed int operation ()
{
  int menuin, action_file;
  char selection, action;

  printf ("[d] delete [m] move [s] skip\n");
  printf ("Enter action (d/m) and file index, or s to skip: ");

  while ((menuin = getchar ()) != '\n') {
    selection = (char)menuin;
    if (selection == 'd' || selection == 'm' || selection == 's')
      action = selection;
    else if (menuin > 47 && menuin < 58)
      action_file = menuin - 48;
    else
      continue;
  }

  if (action == 'd') {
    return action_file;
  }
  else if (action == 'm') {
    return 0 - action_file;
  }
  else if (action == 's')
    return 0;
}

signed int hash_func (dunode *du, char *filename)
{
  return 0;
}

void usage ()
{
  fprintf (stderr, "usage: %s [-p] [directory]\n", programName);
  return;
}

int main (int argc, char *argv[])
{
  programName = malloc (sizeof (argv[0]));
  strcpy (programName, argv[0]);

  getcwd (directory, sizeof (directory));

  /* get options */
  int i;
  for (i = 1; i < argc; i++) {
    if (argv[i][0] == '-') {
      switch (argv[i][1]) {
      case 'p':
	prompt = 1;
	break;
      default:
	fprintf (stderr, "Unknown option: %s\n", argv[i]);
	return 1;
      }
    }
    else { /* is directory argument */
      strcpy (directory, argv[i]);
    }
  }

  printf ("directory = %s\n", directory);

  /* set up linked list of files */
  filenode* firstFileNode = NULL;
  filenode* newFileNode = malloc (sizeof (filenode));
  if (newFileNode == NULL) {
    fprintf (stderr, "Error allocating memory.\n");
    return;
  }

  if (firstFileNode == NULL) {
    firstFileNode = newFileNode;
  }

  filenode* filewalker = firstFileNode;

  /* set up linked list for duplicates */
  dunode* firstDupeNode = NULL;
  dunode* newDupeNode = malloc (sizeof (dunode));
  initialize (newDupeNode);

  if (newDupeNode == NULL) {
    fprintf (stderr, "Error allocating memory.\n");
    return;
  }

  if (firstDupeNode == NULL) {
    firstDupeNode = newDupeNode;
  }

  /* get list of files */
  DIR *dir;
  FILE *fp;
  size_t file_size;
  int file_count = 0;
  struct dirent *ent;
  struct stat *fileattr = malloc (sizeof (struct stat));

  dir = opendir (directory);
  while ((ent = readdir (dir)) != NULL) {
    ++file_count;
    if (stat (ent->d_name, fileattr) == 0) {
      if (S_ISDIR (fileattr->st_mode) != 0)
	continue; /* skip directories */

      strcpy (filewalker->file_name, ent->d_name);
      file_size = fileattr->st_size; /* get file size */
      filewalker->file_size = file_size; /* redundant? */

      /* if no node in dus with file_size, add node to dus, */
      duwalker = firstDupeNode;
      while (duwalker != NULL) {
	if (duwalker->size == file_size) {
	  if (build_du_list (filewalker, file_size,
			  duwalker) == -1) {
	    fprintf (stderr, "Error adding file %s to list of duplicates\n",
		    filewalker->file_name);
	  }
	  break;
	}
	else if (duwalker->next == NULL) { /* last node and still not found */
	  /* add next node, with size */
	  duwalker->next = malloc (sizeof (dunode));
	  initialize (duwalker->next);
	  duwalker->next->size = file_size;
	  if (build_du_list (filewalker, file_size,
			  duwalker->next) == -1) {
	    fprintf (stderr, "Error adding file %s to list of duplicates\n",
		    filewalker->file_name);
	  }
	  break;
	}
	else /* not last node, but not found yet */
	  duwalker = duwalker->next;
	  continue;
      }

      filewalker->next = malloc (sizeof (filenode));
    }
    else
      fprintf (stderr, "Cannot stat file %s: %s\n", filewalker->file_name,
	      strerror (errno));

    filewalker = filewalker->next;
  }
  closedir (dir);
  free (fileattr);

  /* output list of duplicate files */
  duwalker = firstDupeNode;
  int n;
  signed int du_action;
  while (duwalker->next != NULL) {
    if (duwalker->num_dus > 1) {
      printf ("For size %d (%d):\n", duwalker->size, duwalker->num_dus);
      for (n = 0; n < duwalker->num_dus; n++) {
	printf ("%d:\t%s\n", n + 1, duwalker->duplicates[n]->file_name);
      }
      if (prompt == 1) {
	du_action = operation ();
	if (du_action > 0) { /* delete */
	  printf ("Deleting file %s...\n",
		  duwalker->duplicates[du_action - 1]->file_name);
	  /* remove (duwalker->duplicates[du_action -1]->file_name); */
	}
	else if (du_action < 0) { /* move */
	  printf ("Moving file %s...\n",
		  duwalker->duplicates[(du_action + ((0 - du_action) * 2)) - 1]->file_name);
	}
	else {
	  printf ("Skipping.\n");
	}
      }

      printf ("\n");
    }

    duwalker = duwalker->next;
  }

  /* cleanup */
  free (newDupeNode);
  free (newFileNode);
  free (filewalker);
  free (duwalker);
  return 0;
}

