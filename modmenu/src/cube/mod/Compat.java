package cube.mod;

import android.telephony.TelephonyManager;

/**
 * Platform calls that newer Android refuses without READ_PHONE_STATE. When the game runs with a
 * current targetSdk, the SDKs bundled with it crash on a SecurityException.
 * Smali call sites are redirected here.
 */
public final class Compat {
    private Compat() {}

    public static int networkType(TelephonyManager tm) {
        try {
            return tm.getNetworkType();
        } catch (RuntimeException e) {
            return TelephonyManager.NETWORK_TYPE_UNKNOWN;
        }
    }
}
