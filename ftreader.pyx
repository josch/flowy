#cimport libc.stdio
#cimport posix.fcntl

cdef extern from "ftlib.h":
    ctypedef unsigned long long u_int64
    ctypedef unsigned int u_int32
    ctypedef unsigned short u_int16
    ctypedef unsigned char u_int8

    struct fts3rec_all:
          u_int32 *unix_secs
          u_int32 *unix_nsecs
          u_int32 *sysUpTime
          u_int32 *exaddr
          u_int32 *srcaddr
          u_int32 *dstaddr
          u_int32 *nexthop
          u_int16 *input
          u_int16 *output
          u_int32 *dFlows
          u_int32 *dPkts
          u_int32 *dOctets
          u_int32 *First
          u_int32 *Last
          u_int16 *srcport
          u_int16 *dstport
          u_int8  *prot
          u_int8  *tos
          u_int8  *tcp_flags
          u_int8  *engine_type
          u_int8  *engine_id
          u_int8  *src_mask
          u_int8  *dst_mask
          u_int16 *src_as
          u_int16 *dst_as
          u_int8  *in_encaps
          u_int8  *out_encaps
          u_int32 *peer_nexthop
          u_int32 *router_sc
          u_int32 *src_tag
          u_int32 *dst_tag
          u_int32 *extra_pkts
          u_int8  *marked_tos

    struct ftio:
        pass

    struct fts3rec_offsets:
        pass

    struct ftver:
        pass

    cdef enum ft_xfields:
        FT_XFIELD_UNIX_SECS    = 0x0000000000000001LL
        FT_XFIELD_UNIX_NSECS   = 0x0000000000000002LL
        FT_XFIELD_SYSUPTIME    = 0x0000000000000004LL
        FT_XFIELD_EXADDR       = 0x0000000000000008LL
        FT_XFIELD_DFLOWS       = 0x0000000000000010LL
        FT_XFIELD_DPKTS        = 0x0000000000000020LL
        FT_XFIELD_DOCTETS      = 0x0000000000000040LL
        FT_XFIELD_FIRST        = 0x0000000000000080LL
        FT_XFIELD_LAST         = 0x0000000000000100LL
        FT_XFIELD_ENGINE_TYPE  = 0x0000000000000200LL
        FT_XFIELD_ENGINE_ID    = 0x0000000000000400LL
        FT_XFIELD_SRCADDR      = 0x0000000000001000LL
        FT_XFIELD_DSTADDR      = 0x0000000000002000LL
        FT_XFIELD_NEXTHOP      = 0x0000000000010000LL
        FT_XFIELD_INPUT        = 0x0000000000020000LL
        FT_XFIELD_OUTPUT       = 0x0000000000040000LL
        FT_XFIELD_SRCPORT      = 0x0000000000080000LL
        FT_XFIELD_DSTPORT      = 0x0000000000100000LL
        FT_XFIELD_PROT         = 0x0000000000200000LL
        FT_XFIELD_TOS          = 0x0000000000400000LL
        FT_XFIELD_TCP_FLAGS    = 0x0000000000800000LL
        FT_XFIELD_SRC_MASK     = 0x0000000001000000LL
        FT_XFIELD_DST_MASK     = 0x0000000002000000LL
        FT_XFIELD_SRC_AS       = 0x0000000004000000LL
        FT_XFIELD_DST_AS       = 0x0000000008000000LL
        FT_XFIELD_IN_ENCAPS    = 0x0000000010000000LL
        FT_XFIELD_OUT_ENCAPS   = 0x0000000020000000LL
        FT_XFIELD_PEER_NEXTHOP = 0x0000000040000000LL
        FT_XFIELD_ROUTER_SC    = 0x0000000080000000LL
        FT_XFIELD_EXTRA_PKTS   = 0x0000000100000000LL
        FT_XFIELD_MARKED_TOS   = 0x0000000200000000LL
        FT_XFIELD_SRC_TAG      = 0x0000000400000000LL
        FT_XFIELD_DST_TAG      = 0x0000000800000000LL

cdef extern from "include/ftreader.h":
    struct ft_data:
        int fd
        ftio io
        fts3rec_offsets offsets
        ftver version
        u_int64 xfield
        int rec_size
        char **records
        int numrecords

    ft_data *ft_open(char *filename)
    void ft_write(ft_data *data, char *filename)
    void ft_records_get_all(ft_data* data, int number, fts3rec_all *record)
    u_int32 *ft_records_get_unix_secs(ft_data* data, int number)
    u_int32 *ft_records_get_unix_nsecs(ft_data* data, int number)
    u_int32 *ft_records_get_sysUpTime(ft_data* data, int number)
    u_int32 *ft_records_get_exaddr(ft_data* data, int number)
    u_int32 *ft_records_get_srcaddr(ft_data* data, int number)
    u_int32 *ft_records_get_dstaddr(ft_data* data, int number)
    u_int32 *ft_records_get_nexthop(ft_data* data, int number)
    u_int16 *ft_records_get_input(ft_data* data, int number)
    u_int16 *ft_records_get_output(ft_data* data, int number)
    u_int32 *ft_records_get_dFlows(ft_data* data, int number)
    u_int32 *ft_records_get_dPkts(ft_data* data, int number)
    u_int32 *ft_records_get_dOctets(ft_data* data, int number)
    u_int32 *ft_records_get_First(ft_data* data, int number)
    u_int32 *ft_records_get_Last(ft_data* data, int number)
    u_int16 *ft_records_get_srcport(ft_data* data, int number)
    u_int16 *ft_records_get_dstport(ft_data* data, int number)
    u_int8  *ft_records_get_prot(ft_data* data, int number)
    u_int8  *ft_records_get_tos(ft_data* data, int number)
    u_int8  *ft_records_get_tcp_flags(ft_data* data, int number)
    u_int8  *ft_records_get_engine_type(ft_data* data, int number)
    u_int8  *ft_records_get_engine_id(ft_data* data, int number)
    u_int8  *ft_records_get_src_mask(ft_data* data, int number)
    u_int8  *ft_records_get_dst_mask(ft_data* data, int number)
    u_int16 *ft_records_get_src_as(ft_data* data, int number)
    u_int16 *ft_records_get_dst_as(ft_data* data, int number)
    u_int8  *ft_records_get_in_encaps(ft_data* data, int number)
    u_int8  *ft_records_get_out_encaps(ft_data* data, int number)
    u_int32 *ft_records_get_peer_nexthop(ft_data* data, int number)
    u_int32 *ft_records_get_router_sc(ft_data* data, int number)
    u_int32 *ft_records_get_src_tag(ft_data* data, int number)
    u_int32 *ft_records_get_dst_tag(ft_data* data, int number)
    u_int32 *ft_records_get_extra_pkts(ft_data* data, int number)
    u_int8  *ft_records_get_marked_tos(ft_data* data, int number)

cdef class FtReader:
    cdef ft_data *data

    def __init__(self, filename):
        self.data = ft_open(filename)

    def get_numrecords(self):
        return self.data.numrecords

    def supports_attr(self, attr):
        if attr == "unix_secs":
            return bool(self.data.xfield & FT_XFIELD_UNIX_SECS)
        elif attr == "unix_nsecs":
            return bool(self.data.xfield & FT_XFIELD_UNIX_NSECS)
        elif attr == "sysUpTime":
            return bool(self.data.xfield & FT_XFIELD_SYSUPTIME)
        elif attr == "exaddr":
            return bool(self.data.xfield & FT_XFIELD_EXADDR)
        elif attr == "srcaddr":
            return bool(self.data.xfield & FT_XFIELD_SRCADDR)
        elif attr == "dstaddr":
            return bool(self.data.xfield & FT_XFIELD_DSTADDR)
        elif attr == "nexthop":
            return bool(self.data.xfield & FT_XFIELD_NEXTHOP)
        elif attr == "input":
            return bool(self.data.xfield & FT_XFIELD_INPUT)
        elif attr == "output":
            return bool(self.data.xfield & FT_XFIELD_OUTPUT)
        elif attr == "dFlows":
            return bool(self.data.xfield & FT_XFIELD_DFLOWS)
        elif attr == "dPkts":
            return bool(self.data.xfield & FT_XFIELD_DPKTS)
        elif attr == "dOctets":
            return bool(self.data.xfield & FT_XFIELD_DOCTETS)
        elif attr == "First":
            return bool(self.data.xfield & FT_XFIELD_FIRST)
        elif attr == "Last":
            return bool(self.data.xfield & FT_XFIELD_LAST)
        elif attr == "srcport":
            return bool(self.data.xfield & FT_XFIELD_SRCPORT)
        elif attr == "dstport":
            return bool(self.data.xfield & FT_XFIELD_DSTPORT)
        elif attr == "prot":
            return bool(self.data.xfield & FT_XFIELD_PROT)
        elif attr == "tos":
            return bool(self.data.xfield & FT_XFIELD_TOS)
        elif attr == "tcp_flags":
            return bool(self.data.xfield & FT_XFIELD_TCP_FLAGS)
        elif attr == "engine_type":
            return bool(self.data.xfield & FT_XFIELD_ENGINE_TYPE)
        elif attr == "engine_id":
            return bool(self.data.xfield & FT_XFIELD_ENGINE_ID)
        elif attr == "src_mask":
            return bool(self.data.xfield & FT_XFIELD_SRC_MASK)
        elif attr == "dst_mask":
            return bool(self.data.xfield & FT_XFIELD_DST_MASK)
        elif attr == "src_as":
            return bool(self.data.xfield & FT_XFIELD_SRC_AS)
        elif attr == "dst_as":
            return bool(self.data.xfield & FT_XFIELD_DST_AS)
        elif attr == "in_encaps":
            return bool(self.data.xfield & FT_XFIELD_IN_ENCAPS)
        elif attr == "out_encaps":
            return bool(self.data.xfield & FT_XFIELD_OUT_ENCAPS)
        elif attr == "peer_nexthop":
            return bool(self.data.xfield & FT_XFIELD_PEER_NEXTHOP)
        elif attr == "router_sc":
            return bool(self.data.xfield & FT_XFIELD_ROUTER_SC)
        elif attr == "src_tag":
            return bool(self.data.xfield & FT_XFIELD_SRC_TAG)
        elif attr == "dst_tag":
            return bool(self.data.xfield & FT_XFIELD_DST_TAG)
        elif attr == "extra_pkts":
            return bool(self.data.xfield & FT_XFIELD_EXTRA_PKTS)
        elif attr == "marked_tos":
            return bool(self.data.xfield & FT_XFIELD_MARKED_TOS)
        else:
            return False

    def get_record(self, num):
        cdef fts3rec_all record
        ft_records_get_all(self.data, num, &record)
        return (record.unix_secs[0],
                record.unix_nsecs[0],
                record.sysUpTime[0],
                record.exaddr[0],
                record.srcaddr[0],
                record.dstaddr[0],
                record.nexthop[0],
                record.input[0],
                record.output[0],
                record.dFlows[0],
                record.dPkts[0],
                record.dOctets[0],
                record.First[0],
                record.Last[0],
                record.srcport[0],
                record.dstport[0],
                record.prot[0],
                record.tos[0],
                record.tcp_flags[0],
                record.engine_type[0],
                record.engine_id[0],
                record.src_mask[0],
                record.dst_mask[0],
                record.src_as[0],
                record.dst_as[0],
                record.in_encaps[0],
                record.out_encaps[0],
                record.peer_nexthop[0],
                record.router_sc[0],
                record.src_tag[0],
                record.dst_tag[0],
                record.extra_pkts[0],
                record.marked_tos[0]
               )

    def get_unix_secs(self, num):
        return ft_records_get_unix_secs(self.data, num)[0]

    def get_unix_nsecs(self, num):
        return ft_records_get_unix_nsecs(self.data, num)[0]

    def get_sysUpTime(self, num):
        return ft_records_get_sysUpTime(self.data, num)[0]

    def get_exaddr(self, num):
        return ft_records_get_exaddr(self.data, num)[0]

    def get_srcaddr(self, num):
        return ft_records_get_srcaddr(self.data, num)[0]

    def get_dstaddr(self, num):
        return ft_records_get_dstaddr(self.data, num)[0]

    def get_nexthop(self, num):
        return ft_records_get_nexthop(self.data, num)[0]

    def get_input(self, num):
        return ft_records_get_input(self.data, num)[0]

    def get_output(self, num):
        return ft_records_get_output(self.data, num)[0]

    def get_dFlows(self, num):
        return ft_records_get_dFlows(self.data, num)[0]

    def get_dPkts(self, num):
        return ft_records_get_dPkts(self.data, num)[0]

    def get_dOctets(self, num):
        return ft_records_get_dOctets(self.data, num)[0]

    def get_First(self, num):
        return ft_records_get_First(self.data, num)[0]

    def get_Last(self, num):
        return ft_records_get_Last(self.data, num)[0]

    def get_srcport(self, num):
        return ft_records_get_srcport(self.data, num)[0]

    def get_dstport(self, num):
        return ft_records_get_dstport(self.data, num)[0]

    def get_prot(self, num):
        return ft_records_get_prot(self.data, num)[0]

    def get_tos(self, num):
        return ft_records_get_tos(self.data, num)[0]

    def get_tcp_flags(self, num):
        return ft_records_get_tcp_flags(self.data, num)[0]

    def get_engine_type(self, num):
        return ft_records_get_engine_type(self.data, num)[0]

    def get_engine_id(self, num):
        return ft_records_get_engine_id(self.data, num)[0]

    def get_src_mask(self, num):
        return ft_records_get_src_mask(self.data, num)[0]

    def get_dst_mask(self, num):
        return ft_records_get_dst_mask(self.data, num)[0]

    def get_src_as(self, num):
        return ft_records_get_src_as(self.data, num)[0]

    def get_dst_as(self, num):
        return ft_records_get_dst_as(self.data, num)[0]

    def get_in_encaps(self, num):
        return ft_records_get_in_encaps(self.data, num)[0]

    def get_out_encaps(self, num):
        return ft_records_get_out_encaps(self.data, num)[0]

    def get_peer_nexthop(self, num):
        return ft_records_get_peer_nexthop(self.data, num)[0]

    def get_router_sc(self, num):
        return ft_records_get_router_sc(self.data, num)[0]

    def get_src_tag(self, num):
        return ft_records_get_src_tag(self.data, num)[0]

    def get_dst_tag(self, num):
        return ft_records_get_dst_tag(self.data, num)[0]

    def get_extra_pkts(self, num):
        return ft_records_get_extra_pkts(self.data, num)[0]

    def get_marked_tos(self, num):
        return ft_records_get_marked_tos(self.data, num)[0]
