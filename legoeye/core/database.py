import sqlite3
import threading
from typing import Optional, Dict, List, Union
from utils.config import Config
from utils.paths import Paths
from utils.logger import Logger

logger = Logger.get_logger(__name__)


class DatabaseError(Exception):
    """Base database exception"""
    
class ConnectionError(DatabaseError):
    """Database connection issues"""
    
class QueryError(DatabaseError):
    """Query execution errors"""
    
class ConstraintError(DatabaseError):
    """Constraint violations"""


# ██████╗░░█████╗░████████╗░█████╗░██████╗░░█████╗░░██████╗███████╗
# ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝
# ██║░░██║███████║░░░██║░░░███████║██████╦╝███████║╚█████╗░█████╗░░
# ██║░░██║██╔══██║░░░██║░░░██╔══██║██╔══██╗██╔══██║░╚═══██╗██╔══╝░░
# ██████╔╝██║░░██║░░░██║░░░██║░░██║██████╦╝██║░░██║██████╔╝███████╗
# ╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝╚═════╝░╚══════╝

# ██╗░░██╗░█████╗░███╗░░██╗██████╗░██╗░░░░░███████╗██████╗░
# ██║░░██║██╔══██╗████╗░██║██╔══██╗██║░░░░░██╔════╝██╔══██╗
# ███████║███████║██╔██╗██║██║░░██║██║░░░░░█████╗░░██████╔╝
# ██╔══██║██╔══██║██║╚████║██║░░██║██║░░░░░██╔══╝░░██╔══██╗
# ██║░░██║██║░░██║██║░╚███║██████╔╝███████╗███████╗██║░░██║
# ╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░╚══════╝╚══════╝╚═╝░░╚═╝


class DBHandler:
    """
    Thread-safe singleton database handler for SQLite operations.
    Stores clip records with:
      - id (TEXT PRIMARY KEY)
      - timestamp (UNIX epoch, int)
      - duration (seconds, float or NULL)
      - framerate (integer)
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)

                # Initialization
                instance.paths = Paths()
                instance._db_path = instance.paths.DB_PATH
                instance.config = Config()
                instance.conn = sqlite3.connect(instance._db_path, check_same_thread=False)
                instance.db_lock = threading.Lock()
                instance._create_table()
                instance._create_index()
                cls._instance = instance

        return cls._instance

    
    # █▀▀ █▀█ █▀▀ ▄▀█ ▀█▀ █▀▀   ▀█▀ ▄▀█ █▄▄ █░░ █▀▀
    # █▄▄ █▀▄ ██▄ █▀█ ░█░ ██▄   ░█░ █▀█ █▄█ █▄▄ ██▄

    def _create_table(self):
        """Create clips table if not exists."""
        with self.db_lock:
            self.conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS clips (
                    id         TEXT PRIMARY KEY,
                    timestamp  INTEGER NOT NULL,
                    duration   REAL,
                    framerate  INTEGER NOT NULL
                )
                '''
            )
            self.conn.commit()



    # █▀▀ █▀█ █▀▀ ▄▀█ ▀█▀ █▀▀   █ █▄░█ █▀▄ █▀▀ ▀▄▀
    # █▄▄ █▀▄ ██▄ █▀█ ░█░ ██▄   █ █░▀█ █▄▀ ██▄ █░█

    def _create_index(self):
        """Create index on timestamp for faster queries."""
        with self.db_lock:
            self.conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_clips_timestamp
                  ON clips(timestamp)
                '''
            )
            self.conn.commit()


    
    # █ █▄░█ █▀ █▀▀ █▀█ ▀█▀   █▀▀ █░░ █ █▀█
    # █ █░▀█ ▄█ ██▄ █▀▄ ░█░   █▄▄ █▄▄ █ █▀▀

    def insert_clip(self,
                    id: str,
                    timestamp: int,
                    duration: Union[float, None],
                ) -> str:
        """
        Insert a new clip.
        :return: the id
        """

        framerate = self.config.framerate

        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO clips (id, timestamp, duration, framerate) VALUES (?, ?, ?, ?)',
                (id, timestamp, duration, framerate)
            )
            self.conn.commit()
            cursor.close()
        return id
    


    # █░█ █▀█ █▀▄ ▄▀█ ▀█▀ █▀▀   █▀▄ █░█ █▀█ ▄▀█ ▀█▀ █ █▀█ █▄░█
    # █▄█ █▀▀ █▄▀ █▀█ ░█░ ██▄   █▄▀ █▄█ █▀▄ █▀█ ░█░ █ █▄█ █░▀█

    def update_duration(self, id: str, duration: Union[float, None]) -> bool:
        """
        Update duration of a clip.
        :return: True if updated.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE clips SET duration = ? WHERE id = ?',
                (duration, id)
            )
            self.conn.commit()
            updated = cursor.rowcount
            cursor.close()
        return updated > 0



    # █▀▀ █▀▀ ▀█▀   █▀▀ █░░ █ █▀█
    # █▄█ ██▄ ░█░   █▄▄ █▄▄ █ █▀▀
    
    def get_clip(self, id: str) -> Optional[Dict[str, Union[int, float, None, bool]]]:
        """
        Retrieve a clip by ID.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id, timestamp, duration, framerate FROM clips WHERE id = ?',
                (id,)
            )
            row = cursor.fetchone()
            cursor.close()
        if row:
            return {'id': row[0], 'timestamp': row[1], 'duration': row[2], 'framerate': row[3]}
        return None

    # █░░ █ █▀ ▀█▀   █▀▀ █░░ █ █▀█ █▀
    # █▄▄ █ ▄█ ░█░   █▄▄ █▄▄ █ █▀▀ ▄█


    def list_clips(self, limit:int, offset:int) -> List[Dict[str, Union[int, float, None]]]:
        """
        List all clips ordered by timestamp ascending.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id, timestamp, duration, framerate FROM clips WHERE duration IS NOT NULL ORDER BY timestamp ASC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = cursor.fetchall()
            cursor.close()
        return [
            {'id': r[0], 'timestamp': r[1], 'duration': r[2], 'framerate': r[3]}
            for r in rows
        ]
    
    def list_null_duration_clips(self)->List[Dict[str, Union[int, float, None]]]:
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                SELECT id, timestamp, duration, framerate
                FROM clips
                WHERE duration IS NULL
                ORDER BY timestamp ASC
                '''
            )
            rows = cursor.fetchall()
            cursor.close()
        return [
            {'id': r[0], 'timestamp': r[1], 'duration': r[2], 'framerate': r[3]}
            for r in rows
        ]



    # █▀▀ █▀▀ ▀█▀   █▀▀ █░░ █ █▀█ █▀   █ █▄░█   █▀█ ▄▀█ █▄░█ █▀▀ █▀▀
    # █▄█ ██▄ ░█░   █▄▄ █▄▄ █ █▀▀ ▄█   █ █░▀█   █▀▄ █▀█ █░▀█ █▄█ ██▄

    def get_clips_in_range(self, start_ts: int, end_ts: int) -> List[Dict[str, Union[int, float, None, bool]]]:
        """
        Retrieve clips overlapping a time window.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                SELECT id, timestamp, duration, framerate
                FROM clips
                WHERE duration IS NOT NULL
                AND timestamp <= ?
                AND (timestamp + duration) >= ?
                ORDER BY timestamp ASC
                ''',
                (end_ts, start_ts)
            )
            rows = cursor.fetchall()
            cursor.close()
        return [
            {'id': r[0], 'timestamp': r[1], 'duration': r[2], 'framerate': r[3]}
            for r in rows
        ]
    


    # █▀▄ █▀▀ █░░ █▀▀ ▀█▀ █▀▀   █▀▀ █░░ █ █▀█
    # █▄▀ ██▄ █▄▄ ██▄ ░█░ ██▄   █▄▄ █▄▄ █ █▀▀

    def delete_clip(self, id: str) -> bool:
        """
        Delete a clip by ID.
        :return: True if deleted.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM clips WHERE id = ?', (id,))
            self.conn.commit()
            deleted = cursor.rowcount
            cursor.close()
        return deleted > 0

    def get_total_clips(self)->int:
        """
        Returns the total number of clips in the database.
        :return: The total count of clips.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            try:
                cursor.execute("SELECT COUNT(id) FROM clips;")
                total_clips = cursor.fetchone()[0]
                logger.info(f"Total number of clips: {total_clips}")
                return total_clips
            except sqlite3.Error as e:
                logger.error(f"Error getting total clips count: {e}")
            finally:
                cursor.close()

    def get_total_duration(self) -> float:
        """
        Returns the total duration of all clips in the database.
        Clips with NULL duration are ignored in the sum.
        :return: The total duration in seconds. Returns 0.0 if no clips or all durations are NULL.
        """
        with self.db_lock:
            cursor = self.conn.cursor()
            try:
                cursor.execute("SELECT SUM(duration) FROM clips;")
                total_duration = cursor.fetchone()[0]
                # SUM returns None if there are no rows or all summed values are NULL
                if total_duration is None:
                    total_duration = 0.0
                logger.info(f"Total duration of clips: {total_duration:.2f} seconds")
                return float(total_duration)
            except sqlite3.Error as e:
                logger.error(f"Error getting total duration: {e}")
                raise QueryError(f"Failed to get total duration: {e}")
            finally:
                cursor.close()

    # █▀▀ █░░ █▀█ █▀ █▀▀
    # █▄▄ █▄▄ █▄█ ▄█ ██▄

    def close(self) -> None:
        """
        Close the database connection.
        """
        with self.db_lock:
            if self.conn:
                self.conn.close()
                self.conn = None


