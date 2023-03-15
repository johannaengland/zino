"""Even-higher-level APIs over PySNMP's high-level APIs"""
import logging
import threading

from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    getCmd,
)

from zino.config.models import PollDevice

_log = logging.getLogger(__name__)

# keep track of variables that need to be local to the current thread
_local = threading.local()


def _get_engine():
    if not getattr(_local, "snmp_engine", None):
        _local.snmp_engine = SnmpEngine()
    return _local.snmp_engine


class SNMP:
    """Represents an SNMP management session for a single device"""

    def __init__(self, device: PollDevice):
        self.device = device

    async def get(self, *object):
        """SNMP-GETs a single value"""
        query = [ObjectType(ObjectIdentity(*object))]
        error_indication, error_status, error_index, var_binds = await getCmd(
            _get_engine(),
            CommunityData(self.device.community, mpModel=self.mp_model),
            UdpTransportTarget((str(self.device.address), self.device.port)),
            ContextData(),
            *query,
        )

        if error_indication:
            _log.error(error_indication)
            return

        if error_status:
            _log.error("%s at %s", error_status.prettyPrint(), error_index and query[int(error_index) - 1][0] or "?")
            return

        for var_bind in var_binds:
            object, value = var_bind
            return value

    @property
    def mp_model(self):
        """Returns the preferred SNMP version of this device as a PySNMP mpModel value"""
        return 1 if self.device.hcounters else 0