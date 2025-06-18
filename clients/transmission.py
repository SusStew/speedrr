import transmission_rpc
from urllib.parse import urlparse
from typing import Union

from helpers.config import SpeedrrConfig, ClientConfig
from helpers.log_loader import logger
from helpers.bit_convert import bit_conv



class transmissionClient:
    def __init__(self, config: SpeedrrConfig, config_client: ClientConfig) -> None:
        self._client_config = config_client
        self._config = config

        logger.debug(f"<transmission|{self._client_config.url}> Connecting to Transmission at {config_client.url}")
        
        u = urlparse(config_client.url)

        if u.scheme not in ('http', 'https'):
            raise Exception(f"<transmission|{self._client_config.url}> Transmission URL must start with http or https")
        
        try:
            self._client = transmission_rpc.Client(
                protocol=u.scheme,
                username=config_client.username,
                password=config_client.password,
                host=u.hostname,
                port=u.port or 9091,
                path=u.path or '/transmission/rpc'
            )

        except transmission_rpc.error.TransmissionAuthError:
            raise Exception(f"<transmission|{self._client_config.url}> Failed to login to Transmission, check your credentials")

        logger.debug(f"<transmission|{self._client_config.url}> Connected to Transmission")

    def get_active_torrent_count(self) -> int:
        "Get the number of torrents that are currently downloading or uploading."

        logger.debug(f"<transmission|{self._client_config.url}> Getting active torrent count")

        return sum(
            1 for torrent in self._client.get_torrents(arguments=('status',))
            if torrent.status.downloading or torrent.status.seeding
        )


    def set_upload_speed(self, speed: Union[int, float]) -> None:
        "Set the upload speed limit for the client, in config units."

        logger.debug(f"<transmission|{self._client_config.url}> Setting upload speed to {speed}{self._config.units}")
        self._client.set_session(
            speed_limit_up=max(1, int(bit_conv(speed, self._config.units, 'KiB'))),
            speed_limit_up_enabled=True
        )

    def set_download_speed(self, speed: Union[int, float]) -> None:
        "Set the download speed limit for the client, in config units."

        logger.debug(f"<transmission|{self._client_config.url}> Setting download speed to {speed}{self._config.units}")
        self._client.set_session(
            speed_limit_down=max(1, int(bit_conv(speed, self._config.units, 'KiB'))),
            speed_limit_down_enabled=True
        )
