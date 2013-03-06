#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <getopt.h>
#include <sys/select.h>
#include <sys/time.h>
#include <glib.h>

#include <lcm/lcm.h>
#include <bot_param/param_client.h>
#include "lcm_util.h"

#include "../param_client/misc_utils.h"
#include "../param_client/param_internal.h"

#include <lcmtypes/bot2_param.h>

typedef struct {
  BotParam * params;
  lcm_t * lcm;
  int64_t id;
  int32_t seqNo;

  gchar *update_channel;
  gchar *request_channel;
  gchar *set_channel;
} param_server_t;

void publish_params(param_server_t *self)
{

  bot_param_update_t * update_msg = (bot_param_update_t *) calloc(1, sizeof(bot_param_update_t));

  int ret = bot_param_write_to_string(self->params, &update_msg->params);
  if (ret) {
    fprintf(stderr, "ERROR: could not write message to string");
    exit(1);
  }

  update_msg->utime = _timestamp_now();
  update_msg->server_id = self->id;
  update_msg->sequence_number = self->seqNo;

  bot_param_update_t_publish(self->lcm, self->update_channel, update_msg);
  bot_param_update_t_destroy(update_msg);

  fprintf(stderr, ".");
}

void on_param_request(const lcm_recv_buf_t *rbuf, const char * channel, const bot_param_request_t * msg, void * user)
{
  param_server_t * self = (param_server_t*) user;
  publish_params(self);
}

void on_param_update(const lcm_recv_buf_t *rbuf, const char * channel, const bot_param_update_t * msg, void * user)
{
  param_server_t * self = (param_server_t*) user;
  if (msg->server_id != self->id) {
    //TODO: deconfliction of multiple param servers
    fprintf(stderr, "WARNING: Multiple param servers detected!\n");
  }
}

void on_param_set(const lcm_recv_buf_t *rbuf, const char * channel, const bot_param_set_t * msg, void * user)
{
  param_server_t * self = (param_server_t*) user;

  fprintf(stderr, "\ngot param set message whith the following keys:\n");
  for (int i=0;i<msg->numEntries;i++){
    fprintf(stderr,"%s = %s\n", msg->entries[i].key, msg->entries[i].value);

    if (bot_param_set_str(self->params, msg->entries[i].key, msg->entries[i].value) > 0) {
      self->seqNo++;
      publish_params(self);
    }
    else {
      fprintf(stderr, "error: could not set param (%s,%s)!\n", msg->entries[i].key, msg->entries[i].value);
    }
  }

}

static gboolean on_timer(gpointer user)
{
  param_server_t * self = (param_server_t*) user;
  publish_params(self);
  return TRUE;
}

static void usage(int argc, char ** argv)
{
    fprintf(stderr, "Usage: %s [options] <param_file>\n"
            "Parameter Server: Maintains and publishes params initially read from param_file config file\n"
            "\n"
            "Options:\n"
            "   -h, --help          print this help and exit\n"
            "   -s, --server-name   publishes params from named server\n"
            "   -l, --lcm-url       Use this specified LCM URL\n"
            "\n"
            , argv[0]);
}

int main(int argc, char ** argv)
{

  if (argc < 2) {
      usage (argc, argv);
      exit(1);
  }

  param_server_t * self = calloc(1, sizeof(param_server_t));
  GMainLoop * mainloop = g_main_loop_new(NULL, FALSE);
  if (!mainloop) {
      fprintf (stderr, "Error getting the GLIB main loop\n");
      exit(1);
  }


  char *optstring = "hs:l:";
  struct option long_opts[] = {
      { "help", no_argument, NULL, 'h' },
      { "server-name", required_argument, NULL, 's' },
      { "lcm-url", required_argument, NULL, 'l' },
      { 0, 0, 0, 0 }
  };
  int c=-1;
  char *param_prefix = NULL;
  char *lcm_url = NULL;
  while ((c = getopt_long (argc, argv, optstring, long_opts, 0)) >= 0)
  {
      switch (c) {
      case 's':
          param_prefix = optarg;
          break;
      case 'l':
          lcm_url = optarg;
          break;
      case 'h':
      default:
          usage (argc, argv);
          return 1;
      }
  }
  
  self->lcm = lcm_create(lcm_url);
  lcmu_glib_mainloop_attach_lcm(self->lcm);
  

  self->seqNo = 0;
  self->id = _timestamp_now();
  self->params = bot_param_new_from_file(argv[optind]);
  if (self->params==NULL){
    fprintf(stderr, "Could not load params from %s\n", argv[optind]);
    exit(1);
  }
  else
    fprintf(stderr, "Loaded params from %s\n", argv[optind]);

  // set channels here
  if (!param_prefix) param_prefix = getenv ("BOT_PARAM_SERVER_NAME");
  self->update_channel = g_strconcat (param_prefix ? : "", 
          BOT_PARAM_UPDATE_CHANNEL, NULL);
  self->request_channel = g_strconcat (param_prefix ? : "", 
          BOT_PARAM_REQUEST_CHANNEL, NULL);
  self->set_channel = g_strconcat (param_prefix ? : "", 
          BOT_PARAM_SET_CHANNEL, NULL);

  bot_param_update_t_subscribe(self->lcm, self->update_channel, on_param_update, (void *) self);
  bot_param_request_t_subscribe(self->lcm, self->request_channel, on_param_request, (void *) self);
  bot_param_set_t_subscribe(self->lcm, self->set_channel, on_param_set, (void *) self);

  //timer to always publish params every 5sec
  g_timeout_add_full(G_PRIORITY_HIGH, (guint) 5.0 * 1000, on_timer, (gpointer) self, NULL);

  g_main_loop_run(mainloop);

  return 0;
}
