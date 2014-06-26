#include <ftlib.h>

#ifndef __FTREADER_H
#define __FTREADER_H

/*
struct ft_data_offsets {
    const char *name;
    size_t offset;
    size_t size;
    u_int64 xfield;
};
*/

struct ft_data {
    int fd;
    struct ftio io;
    struct fts3rec_offsets offsets;
    struct ftver version;
    u_int64 xfield;
    int rec_size;
    char **records;
    int numrecords;
};

struct ft_data *ft_open(char *filename);
void ft_write(struct ft_data *data, char *filename);

void ft_records_get_all(struct ft_data* data, int number, struct fts3rec_all *record);

u_int32 *ft_records_get_unix_secs(struct ft_data* data, int number);
u_int32 *ft_records_get_unix_nsecs(struct ft_data* data, int number);
u_int32 *ft_records_get_sysUpTime(struct ft_data* data, int number);
u_int32 *ft_records_get_exaddr(struct ft_data* data, int number);
u_int32 *ft_records_get_srcaddr(struct ft_data* data, int number);
u_int32 *ft_records_get_dstaddr(struct ft_data* data, int number);
u_int32 *ft_records_get_nexthop(struct ft_data* data, int number);
u_int16 *ft_records_get_input(struct ft_data* data, int number);
u_int16 *ft_records_get_output(struct ft_data* data, int number);
u_int32 *ft_records_get_dFlows(struct ft_data* data, int number);
u_int32 *ft_records_get_dPkts(struct ft_data* data, int number);
u_int32 *ft_records_get_dOctets(struct ft_data* data, int number);
u_int32 *ft_records_get_First(struct ft_data* data, int number);
u_int32 *ft_records_get_Last(struct ft_data* data, int number);
u_int16 *ft_records_get_srcport(struct ft_data* data, int number);
u_int16 *ft_records_get_dstport(struct ft_data* data, int number);
u_int8  *ft_records_get_prot(struct ft_data* data, int number);
u_int8  *ft_records_get_tos(struct ft_data* data, int number);
u_int8  *ft_records_get_tcp_flags(struct ft_data* data, int number);
u_int8  *ft_records_get_engine_type(struct ft_data* data, int number);
u_int8  *ft_records_get_engine_id(struct ft_data* data, int number);
u_int8  *ft_records_get_src_mask(struct ft_data* data, int number);
u_int8  *ft_records_get_dst_mask(struct ft_data* data, int number);
u_int16 *ft_records_get_src_as(struct ft_data* data, int number);
u_int16 *ft_records_get_dst_as(struct ft_data* data, int number);
u_int8  *ft_records_get_in_encaps(struct ft_data* data, int number);
u_int8  *ft_records_get_out_encaps(struct ft_data* data, int number);
u_int32 *ft_records_get_peer_nexthop(struct ft_data* data, int number);
u_int32 *ft_records_get_router_sc(struct ft_data* data, int number);
u_int32 *ft_records_get_src_tag(struct ft_data* data, int number);
u_int32 *ft_records_get_dst_tag(struct ft_data* data, int number);
u_int32 *ft_records_get_extra_pkts(struct ft_data* data, int number);
u_int8  *ft_records_get_marked_tos(struct ft_data* data, int number);

void ft_close(struct ft_data* data);

#endif
