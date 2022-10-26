from dataclasses import dataclass



# following the standard defined in: https://wiki.ros.org/urdf/XML/joint
@dataclass
class JointStandard:
    joint_types = ['revolute', 'prismatic', 'continuous', 'fixed', 'floating', 'planar']
    joint_type_explanations = ['a hinge joint that rotates along the axis and has a limited range specified by the upper and lower limits.',
                                'a sliding joint that slides along the axis, and has a limited range specified by the upper and lower limits.',
                                'a continuous hinge joint that rotates around the axis and has no upper and lower limits.',
                                'this is not really a joint because it cannot move. All degrees of freedom are locked. This type of joint does not require the <axis>, <calibration>, <dynamics>, <limits> or <safety_controller>.',
                                'this joint allows motion for all 6 degrees of freedom.',
                                'this joint allows motion in a plane perpendicular to the axis.']
    joint_types_and_explanations = {}
    assert len(joint_types) == len(joint_type_explanations), f"The length of the joints types ({len(joint_types)}) is not the same as the length of the joint type explanations ({len(joint_type_explanations)}). There is an error in the implemented standard of the joints."
    for i in range(len(joint_types)):
        joint_types_and_explanations[joint_types[i]] = joint_type_explanations[i]