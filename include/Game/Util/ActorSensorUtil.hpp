#pragma once

#include <JSystem/JGeometry/TVec.hpp>
#include <revolution.h>

class LiveActor;
class HitSensor;

enum {
    ATYPE_PLAYER_START = 0x0,
    ATYPE_PLAYER = 0x1,
    ATYPE_PUPPETEER = 0x2,
    ATYPE_PLAYER_END = 0x3,
    ATYPE_NPC_START = 0x4,
    ATYPE_NPC = 0x5,
    ATYPE_NPC_END = 0x6,
    ATYPE_ANIMAL = 0x7,
    ATYPE_RIDE_START = 0x8,
    ATYPE_RIDE = 0x9,
    ATYPE_SPHERE_PLAYER = 0xA,
    ATYPE_SPHERE_PLAYER_HIT = 0xB,
    ATYPE_SPRING_ATTACKER = 0xC,
    ATYPE_SPRING_ATTACKER_KINOPIO = 0xD,
    ATYPE_SPRING_ATTACKER_KINOPIO_BIND = 0xE,
    ATYPE_JET_TURTLE = 0xF,
    ATYPE_JET_TURTLE_SLOW = 0x10,
    ATYPE_SPECIAL_WEAPON = 0x11,
    ATYPE_RIDE_END = 0x12,
    ATYPE_ENEMY_START = 0x13,
    ATYPE_ENEMY = 0x14,
    ATYPE_ENEMY_SIMPLE = 0x19,
    ATYPE_ENEMY_ATTACK = 0x16,
    ATYPE_COCO_NUT = 0x17,
    ATYPE_WATER_PRESSURE_BULLET = 0x18,
    ATYPE_BOMBHEI = 0x19,
    ATYPE_TAKOBO = 0x1A,
    ATYPE_KURIBO = 0x1B,
    ATYPE_KARIKARI = 0x1C,
    ATYPE_BEGOMAN = 0x1D,
    ATYPE_KILLER_TARGET_ENEMY = 0x1E,
    ATYPE_PLAYER_AUTO_JUMP = 0x23,
    ATYPE_MOGUCCHI_REFUSE_TERRITORY = 0x20,
    ATYPE_BIG_BUBBLE = 0x21,
    ATYPE_NOKONOKO = 0x22,
    ATYPE_PUKUPUKU = 0x23,
    ATYPE_UNIZO = 0x24,
    ATYPE_SAMBO_HEAD = 0x25,
    ATYPE_SAMBO_BODY = 0x26,
    ATYPE_HOMING_FIRE = 0x27,
    ATYPE_HOMING_FIRE_SHOOTER = 0x28,
    ATYPE_HOMING_KILLER = 0x29,
    ATYPE_ROCK = 0x2A,
    ATYPE_WANWAN = 0x2B,
    ATYPE_TRIPODBOSS_GUARD_WALL = 0x2C,
    ATYPE_TRIPODBOSS_KILLER_GENERATER = 0x2D,
    ATYPE_TOMB_SPIDER_BODY = 0x2E,
    ATYPE_TOMB_SPIDER_EYE = 0x2F,
    ATYPE_TOMB_SPIDER_HIP = 0x30,
    ATYPE_TOMB_SPIDER_MOUTH = 0x31,
    ATYPE_TOMB_SPIDER_ATTACKER = 0x32,
    ATYPE_TOMB_SPIDER_GLAND_FRONT_L = 0x33,
    ATYPE_TOMB_SPIDER_GLAND_FRONT_L_ATTACKER = 0x34,
    ATYPE_TOMB_SPIDER_GLAND_FRONT_R = 0x35,
    ATYPE_TOMB_SPIDER_GLAND_FRONT_R_ATTACKER = 0x36,
    ATYPE_TOMB_SPIDER_GLAND_REAR_L = 0x37,
    ATYPE_TOMB_SPIDER_GLAND_REAR_L_ATTACKER = 0x38,
    ATYPE_TOMB_SPIDER_GLAND_REAR_R = 0x39,
    ATYPE_TOMB_SPIDER_GLAND_REAR_R_ATTACKER = 0x3A,
    ATYPE_TOMB_SPIDER_VITAL_SPOT_C = 0x3B,
    ATYPE_TOMB_SPIDER_VITAL_SPOT_L = 0x3C,
    ATYPE_TOMB_SPIDER_VITAL_SPOT_R = 0x3D,
    ATYPE_TOMB_SPIDER_COCOON = 0x3E,
    ATYPE_SAND_GOLEM_BLOCK = 0x3F,
    ATYPE_SAND_GOLEM = 0x40,
    ATYPE_KOOPA_ATTACK = 0x41,
    ATYPE_KOOPA_FIRE = 0x42,
    ATYPE_KOOPA_BALL = 0x43,
    ATYPE_ENEMY_END = 0x44,
    ATYPE_MAPOBJ_START = 0x45,
    ATYPE_MAP_OBJ = 0x46,
    ATYPE_MAP_OBJ_SIMPLE = 0x41,
    ATYPE_MAP_OBJ_MOVE_COLLISION = 0x48,
    ATYPE_CLIP_FIELD_MAP_PARTS = 0x49,
    ATYPE_COIN = 0x44,
    ATYPE_COIN_RED = 0x4B,
    ATYPE_STAR_PIECE = 0x46,
    ATYPE_KINOKO_ONEUP = 0x4D,
    ATYPE_COINTHROW = 0x4E,
    ATYPE_SWITCH = 0x4F,
    ATYPE_MORPH_ITEM = 0x50,
    ATYPE_GOLF_CUP = 0x51,
    ATYPE_BREAKABLE_CAGE = 0x52,
    ATYPE_BEE_FLOWER = 0x53,
    ATYPE_KILLER_TARGET_MAPOBJ = 0x54,
    ATYPE_PUNCH_BOX = 0x55,
    ATYPE_WATER_BAZOOKA_CAPSULE = 0x56,
    ATYPE_ICEJUMP_WALL = 0x57,
    ATYPE_KEY_SWITCH_AVOID = 0x58,
    ATYPE_KAMECK_BARRIER = 0x59,
    ATYPE_KOOPA_PUSH = 0x5A,
    ATYPE_KOOPA_RECEIVER = 0x5B,
    ATYPE_KOOPA_DAMAGE_PLATE = 0x5C,
    ATYPE_KOOPA_COIN_PLATE = 0x5D,
    ATYPE_KOOPA_PLATE = 0x5E,
    ATYPE_MAPOBJ_END = 0x5F,
    ATYPE_AUTO_RUSH_OBJ_START = 0x60,
    ATYPE_BINDER = 0x61,
    ATYPE_TRANSFERABLE_BINDER = 0x62,
    ATYPE_PRIOR_BINDER = 0x63,
    ATYPE_SPIN_DRIVER_BIND = 0x64,
    ATYPE_SPIN_CANNON_BIND = 0x65,
    ATYPE_SPHERE_PLAYER_BIND = 0x66,
    ATYPE_POWER_STAR_BIND = 0x67,
    ATYPE_G_CAPTURE_BIND = 0x68,
    ATYPE_SPRING_ATTACKER_BIND = 0x69,
    ATYPE_WATER_PRESSURE_BULLET_BIND = 0x6A,
    ATYPE_MARIO_LAUNCHER_BIND = 0x6B,
    ATYPE_QUESTION_COIN_BIND = 0x6C,
    ATYPE_SCENARIO_STARTER_BIND = 0x6D,
    ATYPE_AUTO_RUSH_OBJ_END = 0x6E,
    ATYPE_RUSH_OBJ_START = 0x6F,
    ATYPE_RUSH_ENEMY = 0x70,
    ATYPE_COCO_NUT_BIND = 0x71,
    ATYPE_TURNIP_BIND = 0x72,
    ATYPE_SWITCH_BIND = 0x73,
    ATYPE_RUSH_OBJ_END = 0x74,
    ATYPE_PRESS_OBJ_START = 0x75,
    ATYPE_MAP_OBJ_PRESS = 0x76,
    ATYPE_PRESS_OBJ_END = 0x77,
    ATYPE_SPHERE_MOVER_OBJ_START = 0x78,
    ATYPE_JUMP_HOLE = 0x79,
    ATYPE_SPHERE_DASH = 0x7A,
    ATYPE_BALL_RAIL = 0x7B,
    ATYPE_SPHERE_MOVER_OBJ_END = 0x7C,
    ATYPE_SPECIAL_START = 0x7D,
    ATYPE_SYSTEM_SENSOR = 0x7E,
    ATYPE_EYE = 0x7A,
    ATYPE_PUSH = 0x80,
    ATYPE_DEMO = 0x81,
    ATYPE_SWITCH_MESSENGER = 0x82,
    ATYPE_MESSAGE_SENSOR = 0x83,
    ATYPE_RECEIVER = 0x84,
    ATYPE_SPECIAL_END = 0x85,
};

namespace MR {
    void setSensorFollowPos(LiveActor* pActor, const char* pSensorName, const TVec3f* rFollowPos);
    void setSensorFollowMtx(LiveActor* pActor, const char* pSensorName, MtxPtr pFollowMtx);

    HitSensor* addHitSensor(LiveActor* pActor, const char* pSensorName, u32 sensorType, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorBinder(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorPriorBinder(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorRide(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorMapObj(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorMapObjSimple(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorMapObjMoveCollision(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorEnemy(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorEnemyAttack(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorNpc(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorEye(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorPush(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f& rOffset);
    HitSensor* addHitSensorPosRide(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f* pPosition,
                                   const TVec3f& rOffset);
    HitSensor* addHitSensorPosMapObj(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f* pPosition,
                                     const TVec3f& rOffset);
    HitSensor* addHitSensorPosEnemyAttack(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, const TVec3f* pPosition,
                                          const TVec3f& rOffset);
    HitSensor* addHitSensorMtx(LiveActor* pActor, const char* pSensorName, u32 sensorType, u16 receiverCount, f32 radius, MtxPtr pMtx,
                               const TVec3f& rOffset);
    HitSensor* addHitSensorMtxRide(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, MtxPtr pMtx, const TVec3f& rOffset);
    HitSensor* addHitSensorMtxEnemy(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, MtxPtr pMtx, const TVec3f& rOffset);
    HitSensor* addHitSensorMtxEnemyAttack(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, MtxPtr pMtx,
                                          const TVec3f& rOffset);
    HitSensor* addHitSensorMtxAnimal(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius, MtxPtr pMtx, const TVec3f& rOffset);
    HitSensor* addHitSensorAtJoint(LiveActor* pActor, const char* pSensorName, const char* pJointName, u32 sensorType, u16 receiverCount, f32 radius,
                                   const TVec3f& rOffset);
    HitSensor* addHitSensorAtJointMapObj(LiveActor* pActor, const char* pSensorName, const char* pJointName, u16 receiverCount, f32 radius,
                                         const TVec3f& rOffset);
    HitSensor* addHitSensorAtJointMapObjSimple(LiveActor* pActor, const char* pSensorName, const char* pJointName, u16 receiverCount, f32 radius,
                                               const TVec3f& rOffset);
    HitSensor* addHitSensorAtJointEnemy(LiveActor* pActor, const char* pSensorName, const char* pJointName, u16 receiverCount, f32 radius,
                                        const TVec3f& rOffset);
    HitSensor* addHitSensorAtJointEnemyAttack(LiveActor* pActor, const char* pSensorName, const char* pJointName, u16 receiverCount, f32 radius,
                                              const TVec3f& rOffset);
    HitSensor* addHitSensorAtJointNpc(LiveActor* pActor, const char* pSensorName, const char* pJointName, u16 receiverCount, f32 radius,
                                      const TVec3f& rOffset);
    HitSensor* addHitSensorCallback(LiveActor* pActor, const char* pSensorName, u32 sensorType, u16 receiverCount, f32 radius);
    HitSensor* addHitSensorCallbackBinder(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius);
    HitSensor* addHitSensorCallbackPriorBinder(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius);
    HitSensor* addHitSensorCallbackRide(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius);
    HitSensor* addHitSensorCallbackMapObj(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius);
    HitSensor* addHitSensorCallbackEnemyAttack(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius);
    HitSensor* addHitSensorCallbackEye(LiveActor* pActor, const char* pSensorName, u16 receiverCount, f32 radius);
    HitSensor* addBodyMessageSensor(LiveActor* pActor, u32 sensorType);
    HitSensor* addBodyMessageSensorReceiver(LiveActor* pActor);
    HitSensor* addBodyMessageSensorMapObj(LiveActor* pActor);
    HitSensor* addBodyMessageSensorMapObjPress(LiveActor* pActor);
    HitSensor* addBodyMessageSensorEnemy(LiveActor* pActor);
    HitSensor* addMessageSensorReceiver(LiveActor* pActor, const char* pSensorName);
    HitSensor* addHitSensorMapObj(LiveActor* pActor, const char* pSensorName);

    bool tryUpdateHitSensorsAll(LiveActor* pActor);
    void updateHitSensorsAll(LiveActor* pActor);

    bool isSensorType(const HitSensor* pSensor, u32 msg);
    void setSensorType(LiveActor* pActor, const char* pSensorName, u32 msg);
    bool isSensorValid(const HitSensor* pSensor);
    HitSensor* getSensorWithIndex(LiveActor* pActor, int index);
    HitSensor* getTaken(const LiveActor* pActor);
    void setSensorPos(HitSensor* pSensor, const TVec3f& rPosition);
    void setSensorPos(LiveActor* pActor, const char* pSensorName, const TVec3f& rPosition);
    void setSensorOffset(LiveActor* pActor, const char* pSensorName, const TVec3f& rOffset);
    f32 getSensorRadius(HitSensor* pSensor);
    f32 getSensorRadius(LiveActor* pActor, const char* pSensorName);
    void setSensorRadius(HitSensor* pSensor, f32 radius);
    void setSensorRadius(LiveActor* pActor, const char* pSensorName, f32 radius);
    void scaleAllSensorRadius(LiveActor* pActor, f32 scale);
    TVec3f& getSensorHostPos(const HitSensor* pSensor);
    TVec3f& getSensorHostGravity(const HitSensor* pSensor);

    void validateHitSensors(LiveActor* pActor);
    void invalidateHitSensors(LiveActor* pActor);
    void validateHitSensor(HitSensor* pSensor);
    void invalidateHitSensor(HitSensor* pSensor);
    void validateHitSensor(LiveActor* pActor, const char* pSensorName);
    void invalidateHitSensor(LiveActor* pActor, const char* pSensorName);
    bool tryValidateHitSensor(LiveActor* pActor, const char* pSensorName);
    bool tryInvalidateHitSensor(LiveActor* pActor, const char* pSensorName);
    void clearHitSensors(LiveActor* pActor);

    s32 getSensorNum(const LiveActor* pActor);
    HitSensor* getSensor(LiveActor* pActor, int index);
    LiveActor* getSensorHost(const HitSensor* pSensor);
    bool isEqualSensor(const HitSensor* pOtherSensor, const LiveActor* pActor, const char* pSensorName);

    bool isSensorPlayer(const HitSensor* pSensor);
    bool isSensorYoshi(const HitSensor* pSensor);
    bool isSensorBinder(const HitSensor* pSensor);
    bool isSensorReceiver(const HitSensor* pSensor);
    bool isSensorRide(const HitSensor* pSensor);
    bool isSensorPlayerOrRide(const HitSensor* pSensor);
    bool isSensorPlayerOrYoshi(const HitSensor* pSensor);
    bool isSensorPlayerOrYoshiOrRide(const HitSensor* pSensor);
    bool isSensorEnemy(const HitSensor* pSensor);
    bool isSensorEnemyAttack(const HitSensor* pSensor);
    bool isSensorNpc(const HitSensor* pSensor);
    bool isSensorMapObj(const HitSensor* pSensor);
    bool isSensorAutoRush(const HitSensor* pSensor);
    bool isSensorRush(const HitSensor* pSensor);
    bool isSensorPressObj(const HitSensor* pSensor);
    bool isSensorEye(const HitSensor* pSensor);
    bool isSensorPush(const HitSensor* pSensor);
    bool isSensorItem(const HitSensor* pSensor);
    bool isSensorGhost(const HitSensor* pSensor);

    bool tryGetItem(HitSensor*, HitSensor*);

    const TVec3f* getSensorPos(const HitSensor* pSensor);
    const TVec3f* getSensorPos(const LiveActor* pActor, const char* pSensorName);
    const TVec3f* tryGetSensorPos(const HitSensor* pSensor);
    const TVec3f* tryGetSensorPos(const LiveActor* pActor, const char* pSensorName);

    void calcSensorDirection(TVec3f* pDirection, const HitSensor* pFromSensor, const HitSensor* pToSensor);
    void calcSensorDirectionNormalize(TVec3f* pDirection, const HitSensor* pFromSensor, const HitSensor* pToSensor);
    void calcSensorDistanceGravity(f32* pDistance, f32* pDot, const HitSensor* pSensorA, const HitSensor* pSensorB, const TVec3f& rGravity);
    f32 calcSensorDistance(const HitSensor* pSensorA, const HitSensor* pSensorB);
    void calcSensorHorizonNormalize(TVec3f* pHorizon, const TVec3f& rGravity, const HitSensor* pFromSensor, const HitSensor* pToSensor);

    HitSensor* getMessageSensor();

    bool sendArbitraryMsg(u32 msg, HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgPush(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgReflect(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgReflectV(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgGorogoroReflect(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgPlayerTrample(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgPlayerPunch(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgInvincibleAttack(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgDrillAttack(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgRockAttack(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgJump(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgTouchJump(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgTaken(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgAwayJump(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgFireDance(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgRushEnd(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgIsRushEnable(HitSensor* pReceiver, HitSensor* pSender);

    bool sendMsgEnemyAttackMsgToDir(u32 msg, HitSensor* pReceiver, HitSensor* pSender, const TVec3f& rDirection);
    bool sendMsgEnemyAttackFlipVeryWeak(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFlipWeak(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFlipWeakJump(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFlip(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFlipToDir(HitSensor* pReceiver, HitSensor* pSender, const TVec3f& rDirection);
    bool sendMsgEnemyAttackFlipJump(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFlipRot(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFlipMaximumToDir(HitSensor* pReceiver, HitSensor* pSender, const TVec3f& rDirection);
    bool sendMsgEnemyAttack(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackOrPush(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackStrong(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackStrongOrPush(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackStrongToDir(HitSensor* pReceiver, HitSensor* pSender, const TVec3f& rDirection);
    bool sendMsgEnemyAttackFire(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFireStrong(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackElectric(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackFreeze(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackExplosion(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackCounterSpin(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackCounterHipDrop(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgLockOnStarPieceShoot(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgStarPieceAttack(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgStarPieceGift(HitSensor* pReceiver, HitSensor* pSender, u32 giftCount);
    bool sendMsgEnemyAttackMaximum(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgEnemyAttackMaximumToDir(HitSensor* pReceiver, HitSensor* pSender, const TVec3f& rDirection);
    bool sendMsgEnemyAttackToBindedSensor(LiveActor* pSenderActor, HitSensor* pSender);
    bool sendMsgEnemyAttackExplosionToBindedSensor(LiveActor* pSenderActor, HitSensor* pSender);
    bool sendMsgEnemyAttackRollToBindedSensor(LiveActor* pSenderActor, HitSensor* pSender);
    bool sendMsgEnemyAttackTrampleDeathToGroundSensor(HitSensor* pSender);

    HitSensor* getDefaultMessageOrActorSensor(LiveActor* pActor);
    bool sendSimpleMsgToActor(u32 msg, LiveActor* pActor);
    bool sendMsgToBindedSensor(u32 msg, LiveActor*, HitSensor*);
    bool sendMsgToBindedSensor(u32 msg, HitSensor*);
    bool sendMsgToGroundSensor(u32 msg, HitSensor*);
    bool sendMsgToWallSensor(u32 msg, HitSensor*);
    bool sendMsgToRoofSensor(u32 msg, HitSensor*);
    bool sendMsgStartDemo(LiveActor* pActor);

    bool sendMsgToEnemyAttackBlow(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgToEnemyAttackRoll(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgToEnemyAttackBlowToDir(HitSensor* pReceiver, HitSensor* pSender, const TVec3f& rDirection);
    bool sendMsgToEnemyAttackTrample(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgToEnemyAttackTrampleDeath(HitSensor* pReceiver, HitSensor* pSender);
    bool sendMsgToEnemyAttackBlowOrTrample(HitSensor* pReceiver, HitSensor* pSender, f32 trampleThreshold);
    bool sendMsgToEnemyAttackShockWave(HitSensor* pReceiver, HitSensor* pSender);

    bool sendMsgToAllLiveActor(u32 msg, LiveActor* pSenderActor);
    bool sendMsgToGroupMember(u32 msg, LiveActor* pGroupActor, HitSensor* pSender, const char* pSensorName);
    bool sendMsgGroupMoveStartToMember(LiveActor* pGroupActor, HitSensor* pSender, const char* pSensorName);
    bool sendMsgGroupMoveStopToMember(LiveActor* pGroupActor, HitSensor* pSender, const char* pSensorName);
    bool sendMsgGroupShowToMember(LiveActor* pGroupActor, HitSensor* pSender, const char* pSensorName);
    bool sendMsgGroupHideToMember(LiveActor* pGroupActor, HitSensor* pSender, const char* pSensorName);
    bool sendMsgExplosionToNearActor(HitSensor* pSender, f32 range);

    bool isInSpinStormRange(u32 msg, HitSensor* pSender, HitSensor* pReceiver, f32 range);
    void receiveItemShowMsg(u32 msg, HitSensor* pSender, HitSensor* pReceiver);
    void receiveItemHideMsg(u32 msg, HitSensor* pSender, HitSensor* pReceiver);

    HitSensor* getGroundSensor(const LiveActor* pActor);
    HitSensor* getRoofSensor(const LiveActor* pActor);
    HitSensor* getWallSensor(const LiveActor* pActor);
    LiveActor* getGroundActor(const LiveActor* pActor);

    bool isMsgPlayerHitAll(u32 msg);
    bool isMsgPlayerHitProjectiles(u32 msg);
    bool isMsgPlayerSpinAttack(u32 msg);
    bool isMsgPlayerSpinAttackOrSupportTico(u32 msg);
    bool isMsgPlayerTrample(u32 msg);
    bool isMsgPlayerHipDrop(u32 msg);
    bool isMsgPlayerHipDropFloor(u32 msg);
    bool isMsgPlayerUpperPunch(u32 msg);
    bool isMsgPlayerKick(u32 msg);
    bool isMsgPlayerJump(u32 msg);
    bool isMsgTaken(u32 msg);
    bool isMsgThrow(u32 msg);
    bool isMsgDamageOrRushDrop(u32 msg);
    bool isMsgWaterDrop(u32 msg);
    bool isMsgJetTurtleAttack(u32 msg);
    bool isMsgYoshiProjectile(u32 msg);
    bool isMsgYoshiEat(u32 msg);
    bool isMsgYoshiProjectileOrEat(u32 msg);
    bool isMsgFireBallAttack(u32 msg);
    bool isMsgSearchlightAttack(u32 msg);
    bool isMsgFreezeAttack(u32 msg);
    bool isMsgInvincibleAttack(u32 msg);
    bool isMsgDrillAttack(u32 msg);
    bool isMsgRockAttack(u32 msg);
    bool isMsgSnowBallAttack(u32 msg);
    bool isMsgSupportTicoSpin(u32 msg);
    bool isMsgAutoRushBegin(u32 msg);
    bool isMsgRushBegin(u32 msg);
    bool isMsgItemRushBegin(u32 msg);
    bool isMsgUpdateBaseMtx(u32 msg);
    bool isMsgRushForceCancel(u32 msg);
    bool isMsgRushCancel(u32 msg);
    bool isMsgRushEnd(u32 msg);
    bool isMsgRushEnable(u32 msg);
    bool isMsgIsRushTakeOver(u32 msg);
    bool isMsgFloorTouch(u32 msg);
    bool isMsgWallTouch(u32 msg);
    bool isMsgCeilTouch(u32 msg);
    bool isMsgItemGet(u32 msg);
    bool isMsgItemPull(u32 msg);
    bool isMsgItemShow(u32 msg);
    bool isMsgItemHide(u32 msg);
    bool isMsgItemNigeroTake(u32 msg);
    bool isMsgItemStartMove(u32 msg);
    bool isMsgItemEndMoveOrDrop(u32 msg);
    bool isMsgItemEndMove(u32 msg);
    bool isMsgItemNigeroDrop(u32 msg);
    bool isMsgItemSupportTicoDrop(u32 msg);
    bool isMsgInhaleBlackHole(u32 msg);
    bool isMsgStartDemo(u32 msg);
    bool isMsgEnemyAttack(u32 msg);
    bool isMsgEnemyAttackFire(u32 msg);
    bool isMsgEnemyAttackFireStrong(u32 msg);
    bool isMsgEnemyAttackElectric(u32 msg);
    bool isMsgExplosionAttack(u32 msg);
    bool isMsgToEnemyAttackBlow(u32 msg);
    bool isMsgToEnemyAttackRoll(u32 msg);
    bool isMsgToEnemyAttackTrample(u32 msg);
    bool isMsgToEnemyAttackTrampleDeath(u32 msg);
    bool isMsgToEnemyAttackShockWave(u32 msg);
    bool isMsgSpinStormRange(u32 msg);
    bool isMsgSuccess(u32 msg);
    bool isMsgRaceReady(u32 msg);
    bool isMsgRaceStart(u32 msg);
    bool isMsgRaceReset(u32 msg);
    bool isMsgLockOnStarPieceShoot(u32 msg);
    bool isMsgBallDashWall(u32 msg);
    bool isMsgBallDashGround(u32 msg);
    bool isMsgStartPowerStarGet(u32 msg);
    bool isMsgTouchPlantItem(u32 msg);
    bool isMsgHitmarkEmit(u32 msg);
    bool isMsgStarPieceAttack(u32 msg);
    bool isMsgStarPieceReflect(u32 msg);
    bool isMsgStarPieceGift(u32 msg);
    bool isMsgStarLightGrow(u32 msg);
    bool isMsgStarLightShrink(u32 msg);
    bool isMsgReflect(u32 msg);
    bool isMsgReflectV(u32 msg);
    bool isMsgGroupMoveStart(u32 msg);
    bool isMsgGroupMoveStop(u32 msg);
    bool isMsgGroupShow(u32 msg);
    bool isMsgGroupHide(u32 msg);

    s32 getStarPieceGiftCount(u32 msg);

    void calcPosBetweenSensors(TVec3f* pPosition, const HitSensor* pSensorA, const HitSensor* pSensorB, f32 offset);
    bool tryForceKillIfMsgStartPowerStarGet(LiveActor* pActor, u32 msg);
};  // namespace MR
